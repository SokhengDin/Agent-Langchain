import time
import json
import uuid
import re
from typing import Callable, Dict, Any, Optional
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.core.logger import color_status_code


class HTTPTrafficLoggerMiddleware(BaseHTTPMiddleware):

    def __init__(
        self,
        app,
        db_session_factory      : Callable[[], Session] = None,
        save_to_database        : bool = False,
        log_request_body        : bool = True,
        log_response_body       : bool = True,
        max_body_size           : int = 10000,
        exclude_paths           : Optional[list] = None,
        exclude_health_checks   : bool = True
    ):
        super().__init__(app)
        self.db_session_factory     = db_session_factory
        self.save_to_database       = save_to_database
        self.log_request_body       = log_request_body
        self.log_response_body      = log_response_body
        self.max_body_size          = max_body_size
        self.exclude_paths          = exclude_paths or []
        self.exclude_health_checks  = exclude_health_checks
        
        if self.exclude_health_checks:
            self.exclude_paths.extend([
                "/health",
                "/healthz", 
                "/ping",
                "/status",
                "/metrics",
                "/docs",
                "/redoc",
                "/openapi.json"
            ])

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id          = str(uuid.uuid4())
        
        if self._should_exclude_path(request.url.path):
            return await call_next(request)

        start_time          = time.time()
        request_time        = datetime.now(timezone.utc)

        await self._log_request(request, request_id)

        request_body        = None
        if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            request_body    = await self._get_request_body(request)

        error_message       = None
        error_class         = None
        
        try:
            response        = await call_next(request)
        except Exception as e:
            processing_time = time.time() - start_time
            error_message   = str(e)
            error_class     = type(e).__name__
            
            logger.error(
                f"Request {request_id} failed | "
                f"{request.method} {request.url.path} | "
                f"Error: {str(e)} | "
                f"Time: {processing_time:.3f}s"
            )
            
            # Database logging disabled for storage reasons
            raise

        processing_time = time.time() - start_time
        response_time   = datetime.now(timezone.utc)

        await self._log_response(request, response, request_id, processing_time, request_body)

        # Extract error details for 4xx/5xx responses
        if response.status_code >= 400:
            error_details       = await self._extract_error_details(response)
            if error_details:
                error_message   = error_details.get('message')
                error_class     = error_details.get('class')

        # Database logging disabled for storage reasons

        return response

    def _should_exclude_path(self, path: str) -> bool:
        return any(excluded in path for excluded in self.exclude_paths)

    async def _log_request(self, request: Request, request_id: str):
        try:
            client_host     = getattr(request.client, 'host', 'unknown') if request.client else 'unknown'
            user_agent      = request.headers.get('user-agent', 'unknown')
        

            logger.info(
                f"→ Request {request_id} | "
                f"{request.method} {request.url.path} | "
                f"Client: {client_host} | "
                f"UA: {user_agent[:50]}{'...' if len(user_agent) > 50 else ''}"
            )
            
            # if query_params:
            #     logger.debug(f"Request {request_id} Query: {query_params}")
                
            headers = self._filter_sensitive_headers(dict(request.headers))
            # logger.debug(f"Request {request_id} Headers: {headers}")
            
        except Exception as e:
            logger.error(f"Error logging request {request_id}: {str(e)}")

    async def _log_response(
        self, 
        request         : Request, 
        response        : Response, 
        request_id      : str, 
        processing_time : float,
        request_body    : Optional[str] = None
    ):
        try:
            colored_status = color_status_code(response.status_code)
            if response.status_code >= 500:
                log_level = logger.error
            elif response.status_code >= 400:
                log_level = logger.warning
            else:
                log_level = logger.info

            log_level(
                f"← Response {request_id} | "
                f"{request.method} {request.url.path} | "
                f"Status: {colored_status} | "
                f"Time: {processing_time:.3f}s"
            )
            
            # if request_body and self.log_request_body:
            #     logger.debug(f"Request {request_id} Body: {request_body}")
            
            response_headers = self._filter_sensitive_headers(dict(response.headers))
            # logger.debug(f"Response {request_id} Headers: {response_headers}")
            
            if self.log_response_body and not isinstance(response, StreamingResponse):
                response_body = await self._get_response_body(response)
                # if response_body:
                #     logger.debug(f"Response {request_id} Body: {response_body}")
                    
        except Exception as e:
            logger.error(f"Error logging response {request_id}: {str(e)}")

    async def _get_request_body(self, request: Request) -> Optional[str]:
        try:
            body = await request.body()
            if len(body) > self.max_body_size:
                return f"[Body too large: {len(body)} bytes, max: {self.max_body_size}]"
            
            if body:
                try:
                    body_dict    = json.loads(body.decode('utf-8'))
                    filtered_body = self._filter_sensitive_data(body_dict)
                    return json.dumps(filtered_body, ensure_ascii=False)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    body_str = body.decode('utf-8', errors='ignore')
                    if len(body_str) > 500:
                        return body_str[:500] + "..."
                    return body_str
            return None
        except Exception as e:
            logger.error(f"Error reading request body: {str(e)}")
            return "[Error reading body]"

    async def _get_response_body(self, response: Response) -> Optional[str]:
        try:
            if hasattr(response, 'body') and response.body:
                body = response.body
                if len(body) > self.max_body_size:
                    return f"[Body too large: {len(body)} bytes, max: {self.max_body_size}]"
                
                try:
                    body_dict = json.loads(body.decode('utf-8'))
                    return json.dumps(body_dict, ensure_ascii=False)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    body_str = body.decode('utf-8', errors='ignore')
                    if len(body_str) > 500:
                        return body_str[:500] + "..."
                    return body_str
            return None
        except Exception as e:
            logger.error(f"Error reading response body: {str(e)}")
            return "[Error reading body]"

    def _filter_sensitive_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        sensitive_headers = {
            'authorization', 'cookie', 'x-api-key', 'x-auth-token', 
            'x-access-token', 'x-refresh-token', 'set-cookie'
        }
        
        filtered = {}
        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                filtered[key] = "[REDACTED]"
            else:
                filtered[key] = value
        return filtered

    def _filter_sensitive_data(self, data: Any) -> Any:
        if isinstance(data, dict):
            sensitive_keys = {
                'password', 'token', 'secret', 'key', 'api_key', 
                'access_token', 'refresh_token', 'auth_token',
                'authorization', 'credential', 'private_key'
            }
            
            filtered = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    filtered[key] = "[REDACTED]"
                else:
                    filtered[key] = self._filter_sensitive_data(value)
            return filtered
        elif isinstance(data, list):
            return [self._filter_sensitive_data(item) for item in data]
        else:
            return data

    async def _save_to_database(
        self,
        request         : Request,
        response        : Optional[Response],
        request_id      : str,
        request_time    : datetime,
        response_time   : datetime,
        duration_ms     : int,
        status_code     : int,
        error_message   : Optional[str] = None,
        error_class     : Optional[str] = None
    ):
        try:
            if not self.db_session_factory:
                return

            # Get client IP with proxy support
            ip_address   = self._get_client_ip(request)
            
            # Clean endpoint path by removing IDs and params
            endpoint     = self._clean_endpoint(request.url.path)
            
            # Detect bot and suspicious traffic
            is_bot          = self._detect_bot(request)
            is_suspicious   = self._detect_suspicious(request, status_code, duration_ms)
            
            # Get response size
            response_size   = None
            response_content_type = None
            if response:
                response_size = int(response.headers.get('content-length', 0)) or None
                response_content_type = response.headers.get('content-type')
            
                
        except Exception as e:
            logger.error(f"Error saving request log to database: {str(e)}")

    def _get_client_ip(self, request: Request) -> str:
        # Check X-Forwarded-For header first
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(',')[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip
        
        # Fall back to client host
        if request.client:
            return request.client.host
        
        return 'unknown'

    def _clean_endpoint(self, path: str) -> str:
        cleaned = path
        
        uuid_pattern    = r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        cleaned         = re.sub(uuid_pattern, '/{uuid}', cleaned, flags=re.IGNORECASE)
        
        numeric_pattern = r'/\d+'
        cleaned         = re.sub(numeric_pattern, '/{id}', cleaned)

        id_pattern  = r'/[a-zA-Z0-9]{10,}'
        cleaned     = re.sub(id_pattern, '/{id}', cleaned)
        
        return cleaned

    def _detect_bot(self, request: Request) -> bool:
        user_agent = request.headers.get('user-agent', '').lower()
        
        bot_indicators = [
            'bot', 'crawler', 'spider', 'scraper', 'fetch', 'curl', 'wget',
            'googlebot', 'bingbot', 'slurp', 'duckduckbot', 'baiduspider',
            'yandexbot', 'facebookexternalhit', 'twitterbot', 'linkedinbot',
            'whatsapp', 'telegram', 'slack', 'python-requests', 'go-http-client',
            'java/', 'apache-httpclient', 'okhttp', 'postman', 'insomnia'
        ]
        
        return any(indicator in user_agent for indicator in bot_indicators)

    def _detect_suspicious(self, request: Request, status_code: int, duration_ms: int) -> bool:
        # Multiple criteria for suspicious activity
        suspicious_factors = 0
        
        # High error rate
        if status_code >= 400:
            suspicious_factors += 1
        
        # Very slow requests (potential attack)
        if duration_ms > 10000:  # > 10 seconds
            suspicious_factors += 1
        

        path                = request.url.path.lower()
        suspicious_paths    = [
            'admin', 'wp-admin', 'phpmyadmin', 'config', '.env',
            'backup', 'sql', 'dump', 'shell', 'cmd', 'eval',
            'script', 'php', 'asp', 'jsp', '/../', '/etc/'
        ]
        if any(sus_path in path for sus_path in suspicious_paths):
            suspicious_factors += 2
        
        # Suspicious headers
        user_agent   = request.headers.get('user-agent', '').lower()
        if not user_agent or len(user_agent) < 5:
            suspicious_factors += 1
        
        # No referer on POST requests (potential CSRF)
        if request.method in ['POST', 'PUT', 'DELETE'] and not request.headers.get('referer'):
            suspicious_factors += 1

        query_string        = str(request.url.query).lower()
        suspicious_params   = ['select', 'union', 'drop', 'insert', 'update', 'delete', 'script', 'alert']
        if sum(1 for param in suspicious_params if param in query_string) >= 2:
            suspicious_factors += 2
    
        return suspicious_factors >= 2

    async def _extract_error_details(self, response: Response) -> Optional[Dict[str, str]]:
        """Extract error message and class from error responses"""
        try:
            if hasattr(response, 'body') and response.body:
                body = response.body
                if isinstance(body, bytes):
                    body_str = body.decode('utf-8')
                    
                    try:
                        import json
                        body_json = json.loads(body_str)
                        
                        # Handle your RESPONSE_SCHEMA format
                        if isinstance(body_json, dict):
                            error_message   = None
                            error_class     = None
                            
                            if 'message' in body_json:
                                error_message = body_json['message']
                            elif 'detail' in body_json:
                                error_message = body_json['detail']
                            elif 'data' in body_json and isinstance(body_json['data'], dict):
                                if 'errors' in body_json['data']:
                                    errors = body_json['data']['errors']
                                    if isinstance(errors, list) and errors:
                                        error_message   = f"Validation: {errors[0].get('message', 'Unknown validation error')}"
                                        error_class     = "ValidationError"
                                else:
                                    error_message = body_json['data'].get('message')
                            if not error_class:
                                if response.status_code == 400:
                                    error_class = "BadRequestError"
                                elif response.status_code == 401:
                                    error_class = "UnauthorizedError"  
                                elif response.status_code == 403:
                                    error_class = "ForbiddenError"
                                elif response.status_code == 404:
                                    error_class = "NotFoundError"
                                elif response.status_code == 422:
                                    error_class = "ValidationError"
                                elif response.status_code >= 500:
                                    error_class = "InternalServerError"
                                else:
                                    error_class = "HTTPError"
                            
                            if error_message:
                                return {
                                    'message': error_message,
                                    'class': error_class
                                }
                                
                    except json.JSONDecodeError:
                        if len(body_str) <= 500:  # Only capture reasonable length messages
                            return {
                                'message': body_str,
                                'class': 'HTTPError'
                            }
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting error details: {str(e)}")
            return None


class HTTPTrafficLoggerConfig:
    
    def __init__(
        self,
        enabled                 : bool = True,
        save_to_database        : bool = False,
        log_request_body        : bool = True,
        log_response_body       : bool = True,
        max_body_size           : int = 10000,
        exclude_paths           : Optional[list] = None,
        exclude_health_checks   : bool = True,
        use_colors              : bool = False 
    ):
        self.enabled                = enabled
        self.save_to_database       = save_to_database
        self.log_request_body       = log_request_body
        self.log_response_body      = log_response_body
        self.max_body_size          = max_body_size
        self.exclude_paths          = exclude_paths or []
        self.exclude_health_checks  = exclude_health_checks
        self.use_colors             = use_colors 