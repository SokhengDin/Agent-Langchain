from typing import Optional, AsyncGenerator
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import json

from app.services.ds_agent_service import DSAgentService
from app import logger

router = APIRouter()

ds_agent_service = DSAgentService()

class DSChatRequest(BaseModel):
    message     : str               = Field(..., description="Student's question or request")
    thread_id   : Optional[str]     = Field(None, description="Thread ID for conversation continuity")

class DSChatResponse(BaseModel):
    response    : str               = Field(..., description="Agent's response")
    thread_id   : str               = Field(..., description="Thread ID for this conversation")

@router.post("/chat", response_model=DSChatResponse, status_code=status.HTTP_200_OK)
async def chat(request: DSChatRequest) -> DSChatResponse:
    """
    Chat with data science agent

    Request:
    {
        "message": "Can you analyze this dataset?",
        "thread_id": "optional-thread-id"
    }

    Response:
    {
        "response": "Agent's response with analysis",
        "thread_id": "thread-uuid"
    }
    """
    try:
        result = await ds_agent_service.handle_conversation(
            message     = request.message
            , thread_id = request.thread_id
        )

        return DSChatResponse(
            response    = result["response"]
            , thread_id = result["thread_id"]
        )

    except Exception as e:
        logger.error(f"Error in DS chat endpoint: {str(e)}")
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            , detail    = f"Error processing chat request: {str(e)}"
        )

@router.post("/chat/stream")
async def chat_stream(request: DSChatRequest):
    """
    Stream chat with data science agent

    Request:
    {
        "message": "Train a linear regression model on my data",
        "thread_id": "optional-thread-id"
    }

    Streaming Events:
    - {"type": "start", "thread_id": "..."}
    - {"type": "thinking", "content": "reasoning content"}
    - {"type": "tool_call", "step": "tools", "tool_calls": [{...}]}
    - {"type": "token", "content": "streaming text"}
    - {"type": "thinking_stats", "reasoning_tokens": 123}
    - {"type": "done", "thread_id": "..."}
    - {"type": "error", "error": "error message"}
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            async for event in ds_agent_service.handle_conversation_stream(
                message     = request.message
                , thread_id = request.thread_id
            ):
                yield f"data: {json.dumps(event)}\n\n"

        except Exception as e:
            logger.error(f"Error in DS chat stream: {str(e)}")
            error_event = {
                "type"  : "error"
                , "error": str(e)
            }
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        event_generator()
        , media_type = "text/event-stream"
        , headers    = {
            "Cache-Control"         : "no-cache"
            , "Connection"          : "keep-alive"
            , "X-Accel-Buffering"   : "no"
        }
    )
