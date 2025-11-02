import httpx
import json

from typing import Optional, Dict, Any, Union
from urllib.parse import urljoin

from app.core.config import settings

from app import logger


class APIUtils:
    
    base_url = settings.API_BASE_URL
    timeout  = 30.0


    @staticmethod
    async def _make_request(
        method    : str
        , endpoint  : str
        , params    : Optional[Dict[str, Any]] = None
        , data      : Optional[Dict[str, Any]] = None
        , headers   : Optional[Dict[str, str]] = None
    ) -> Union[Dict[str, Any], str]:
        """
        Make HTTP request using httpx
        
        Args:
            method  : HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params  : Query parameters
            data    : Request body
            headers : Request headers
            
        Returns:
            Response data
        """
        url = urljoin(APIUtils.base_url, endpoint)
        
        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if headers:
            default_headers.update(headers)
            
        try:
            async with httpx.AsyncClient(timeout=APIUtils.timeout) as client:
                response = await client.request(
                    method      = method
                    , url      = url
                    , params   = params
                    , json     = data
                    , headers  = default_headers
                )
                
                response.raise_for_status()
                
                try:
                    return response.json()
                except UnicodeDecodeError:
                    try:
                        content = response.content
                        if "application/json" in response.headers.get("content-type", ""):
                            return json.loads(content.decode('latin-1'))
                        return content
                    except Exception as decode_error:
                        logger.error(f"Failed to decode response: {str(decode_error)}")
                        raise
            
        except httpx.TimeoutException:
            logger.error(f"Request timeout for {method} {url}")
            raise
        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {method} {url}: {e.response.text}")
            raise
        
        except Exception as e:
            logger.error(f"Error making request to {method} {url}: {str(e)}")
            raise
            
    async def get(
         endpoint  : str
        , params    : Optional[Dict[str, Any]] = None
        , headers   : Optional[Dict[str, str]] = None
    ) -> Union[Dict[str, Any], str]:
        """Send GET request"""
        return await APIUtils._make_request("GET", endpoint, params=params, headers=headers)
    
    async def post(
        endpoint  : str
        , data      : Dict[str, Any]
        , params    : Optional[Dict[str, Any]] = None
        , headers   : Optional[Dict[str, str]] = None
    ) -> Union[Dict[str, Any], str]:
        """Send POST request"""
        return await APIUtils._make_request("POST", endpoint, params=params, data=data, headers=headers)
    
    async def put(
         endpoint  : str
        , data      : Dict[str, Any]
        , params    : Optional[Dict[str, Any]] = None
        , headers   : Optional[Dict[str, str]] = None
    ) -> Union[Dict[str, Any], str]:
        """Send PUT request"""
        return await APIUtils._make_request("PUT", endpoint, params=params, data=data, headers=headers)
    
    async def delete(
        endpoint  : str
        , params    : Optional[Dict[str, Any]] = None
        , headers   : Optional[Dict[str, str]] = None
    ) -> Union[Dict[str, Any], str]:
        """Send DELETE request"""
        return await APIUtils._make_request("DELETE", endpoint, params=params, headers=headers)
    
    async def patch(
        endpoint  : str
        , data      : Dict[str, Any]
        , params    : Optional[Dict[str, Any]] = None
        , headers   : Optional[Dict[str, str]] = None
    ) -> Union[Dict[str, Any], str]:
        """Send PATCH request"""
        return await APIUtils._make_request("PATCH", endpoint, params=params, data=data, headers=headers)