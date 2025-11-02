from fastapi import APIRouter

from app.api.v1.handlers import (
    hotel_agent_handler as hotel_agent_handler_v1
)

router  = APIRouter()

# V1 routes (legacy - OpenAI)
router.include_router(hotel_agent_handler_v1.router     , prefix="/hotel-agent"     , tags=["Hotel Agent V1"])