from functools import lru_cache

from app.services.hotel_agent_service import HotelAgentService


@lru_cache()
def get_hotel_agent_initialized() -> HotelAgentService:
    """
    Initialize and cache the hotel agent service.
    Remove async since we're just instantiating
    """
    service     = HotelAgentService()
    
    return service