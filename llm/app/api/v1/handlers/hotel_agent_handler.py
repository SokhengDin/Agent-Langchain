from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, List, Optional
from pydantic import BaseModel

from app.services.hotel_agent_service import HotelAgentService
from app.api.deps.llm_deps import get_hotel_agent_initialized

from loguru import logger


router = APIRouter()


class Message(BaseModel):
    content     : str

class ConversationRequest(BaseModel):
    message     : str
    thread_id   : str


class ConversationResponse(BaseModel):
    response        : str
    thread_id       : Optional[str] = None



@router.post(
    "/chat"
    , response_model    = ConversationResponse
    , status_code      = status.HTTP_200_OK
)
async def process_conversation(
    request          : ConversationRequest
    , agent_service  : HotelAgentService = Depends(get_hotel_agent_initialized)
) -> ConversationResponse:
    """Process a conversation with memory management"""
    logger.info(
        "Processing conversation request"
        , extra = {"thread_id": request.thread_id}
    )
    
    try:
        response    = await agent_service.handle_conversation(
            message     = request.message
            , thread_id = request.thread_id
        )
        
        logger.info(
            "Conversation processed successfully"
        )
        
        return ConversationResponse(
            response        = response["output"]
            , thread_id     = response["thread_id"]
        )
        
    except Exception as e:
        logger.error(
            f"Error processing conversation: {str(e)}"
            , extra = {"thread_id": request.thread_id}
        )
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            , detail    = str(e)
        )