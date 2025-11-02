from fastapi import APIRouter

from app.api.v2.handlers import (
    hotel_agent_handler as hotel_agent_handler_v2
)

router  = APIRouter()
# V2 routes (LangChain 1.0 + Ollama)
router.include_router(hotel_agent_handler_v2.router     , prefix="/hotel-agent"  , tags=["Hotel Agent V2"])