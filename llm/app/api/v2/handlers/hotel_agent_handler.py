from typing import Optional, Dict, Any, AsyncGenerator
from fastapi import APIRouter, HTTPException, status, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import json

from app.services.hotel_agent_service_v2 import HotelAgentServiceV2
from app import logger


router = APIRouter()

hotel_agent_service = HotelAgentServiceV2()


class ChatRequest(BaseModel):
    message         : str                       = Field(..., description="User message")
    thread_id       : Optional[str]             = Field(None, description="Thread ID for conversation continuity")


class ChatResponse(BaseModel):
    response            : str                       = Field(..., description="Agent response")
    thread_id           : str                       = Field(..., description="Thread ID for this conversation")


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(request: ChatRequest, authorization: Optional[str] = Header(None)) -> ChatResponse:

    try:

        token   = None

        if authorization and authorization.startswith("Bearer "):
            token       = authorization.split(" ")[1]

        result = await hotel_agent_service.handle_conversation(
            message     = request.message
            , thread_id = request.thread_id
            , token     = token
        )

        return ChatResponse(
            response    = result["response"]
            , thread_id = result["thread_id"]
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            , detail    = f"Error processing chat request: {str(e)}"
        )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, authorization: Optional[str] = Header(None)):

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            token = None
            if authorization and authorization.startswith("Bearer "):
                token = authorization.split(" ")[1]

            async for event in hotel_agent_service.handle_conversation_stream(
                message     = request.message
                , thread_id = request.thread_id
                , token     = token
            ):
                yield f"data: {json.dumps(event)}\n\n"

        except Exception as e:
            logger.error(f"Error in chat stream: {str(e)}")
            error_event = {
                "type"      : "error"
                , "error"   : str(e)
            }
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        event_generator()
        , media_type = "text/event-stream"
        , headers    = {
            "Cache-Control"             : "no-cache"
            , "Connection"              : "keep-alive"
            , "X-Accel-Buffering"       : "no"
        }
    )
