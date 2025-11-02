from fastapi import APIRouter

from app.api.v2.handlers import (
    hotel_agent_handler as hotel_agent_handler_v2
    , upload_handler
)

router  = APIRouter()

router.include_router(hotel_agent_handler_v2.router , prefix="/hotel-agent"  , tags=["Hotel Agent V2"])
router.include_router(upload_handler.router         , prefix="/upload"       , tags=["File Upload"])