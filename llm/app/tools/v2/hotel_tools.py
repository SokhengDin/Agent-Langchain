from typing import Dict, List, Optional
from uuid import UUID
from decimal import Decimal

from fastapi import HTTPException, status
from langchain_core.tools import tool
from app.schema.hotel_schema import HotelSearchInput
from app.core.utils.api_utils_sync import APIUtils
from loguru import logger


class HotelTools:
    """Tools for interacting with hotel management system (synchronous version)"""

    @staticmethod
    @tool("search_hotel_tool", args_schema=HotelSearchInput)
    def search_hotels(
        search_term : Optional[str] = None,
        city        : Optional[str] = None,
        min_rating  : Optional[Decimal] = None,
        skip        : int = 0,
        limit       : int = 5
    ) -> List[Dict]:
        """
        Executes hotel search with structured parameters.
        Returns simplified hotel data for LLM processing.
        """
        params = {
            "search_term": search_term if search_term else None,
            "city"      : city if city else None,
            "min_rating": str(min_rating) if min_rating else None,
            "skip"      : skip,
            "limit"     : limit
        }

        try:
            params = {k: v for k, v in params.items() if v is not None}

            logger.info(f"Searching for hotels with params {params}")

            response = APIUtils.get(
                endpoint = "/api/v1/hotel/search",
                params   = params
            )

            return response

        except Exception as e:
            logger.error(f"{str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail      = str(e)
            )

    @staticmethod
    @tool("get_hotel_tool")
    def get_hotel(
        hotel_id: UUID
    ) -> Dict:
        """
        Get hotel details by ID.

        Args:
            hotel_id : UUID of the hotel

        Returns:
            Dict containing hotel information
        """
        try:
            response = APIUtils.get(
                endpoint = f"/api/v1/hotel/{hotel_id}"
            )

            return response

        except Exception as e:
            logger.error(f"Failed to get hotel: {str(e)}")
            raise

    @staticmethod
    @tool("list_hotels_tool")
    def list_hotels(
        skip  : int = 0,
        limit : int = 100
    ) -> List[Dict]:
        """
        Get list of all hotels with pagination.

        Args:
            skip  : Number of records to skip
            limit : Maximum number of records to return

        Returns:
            List of hotel records
        """
        try:
            params = {"skip": skip, "limit": limit}

            response = APIUtils.get(
                endpoint = "/api/v1/hotel/",
                params   = params
            )

            return response

        except Exception as e:
            logger.error(f"Failed to list hotels: {str(e)}")
            raise

    @staticmethod
    @tool("get_hotel_rooms_tool")
    def get_hotel_rooms(
        hotel_id: UUID,
        skip     : int = 0,
        limit    : int = 100
    ) -> List[Dict]:
        """
        Get all rooms for a specific hotel.

        Args:
            hotel_id : UUID of the hotel
            skip     : Number of records to skip
            limit    : Maximum number of records to return

        Returns:
            List of room records for the hotel
        """
        try:
            params = {"skip": skip, "limit": limit}

            response = APIUtils.get(
                endpoint = f"/api/v1/hotel/{hotel_id}/rooms",
                params   = params
            )

            return response

        except Exception as e:
            logger.error(f"Failed to get hotel rooms: {str(e)}")
            raise
