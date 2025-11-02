from typing import Dict, List, Optional
from uuid import UUID

from langchain_core.tools import tool

from app.schema.room_schema import RoomSchemaIn
from app.core.utils.api_utils_sync import APIUtils
from app.core.enum.enum import RoomType

from app import logger

class RoomTools:
    """Tools for managing room operations in the hotel system"""
    
    @staticmethod
    @tool("create_room_tool", args_schema=RoomSchemaIn)
    def create_room(
        hotel_id            : UUID
        , room_number       : str
        , room_type         : RoomType
        , price_per_night   : float
        , floor             : Optional[int] = None
        , status            : str = "AVAILABLE"
        , additional_notes  : Optional[str] = None
    ) -> Dict:
        """
        Create a new room in the hotel system.

        Args:
            hotel_id         : UUID of the hotel
            room_number      : Room number identifier
            room_type        : Type of room (SINGLE_ROOM, DOUBLE_ROOM, TWIN_ROOM, FAMILY_ROOM, SUITE_ROOM)
            price_per_night  : Price per night for the room
            floor            : Floor number
            status           : Room status
            additional_notes : Additional room notes

        Returns:
            Dict containing created room information
        """
        try:
            data = {
                "hotel_id"          : str(hotel_id)
                , "room_number"     : room_number
                , "room_type"       : room_type.value if hasattr(room_type, "value") else room_type
                , "price_per_night" : price_per_night
                , "floor"           : floor
                , "status"          : status
                , "additional_notes": additional_notes
            }

            response = APIUtils.post(
                endpoint = "/api/v1/room"
                , data   = data
            )

            logger.info(
                "Room created successfully"
                , extra = {
                    "hotel_id"     : str(hotel_id)
                    , "room_number": room_number
                }
            )

            return response

        except Exception as e:
            logger.error(f"Failed to create room: {str(e)}")
            raise

    @staticmethod
    @tool("get_room_tool")
    def get_room(
        room_id: UUID
    ) -> Dict:
        """
        Get room details by ID.
        
        Args:
            room_id: UUID of the room
            
        Returns:
            Dict containing room information
        """
        try:
            response = APIUtils.get(
                endpoint = f"/api/v1/room/{room_id}"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get room: {str(e)}")
            raise

    @staticmethod
    @tool("get_hotel_rooms_tool")
    def get_hotel_rooms(
        hotel_id    : UUID
        , room_type : Optional[RoomType] = None
        , floor     : Optional[int] = None
        , status    : Optional[str] = None
        , skip      : int = 0
        , limit     : int = 100
    ) -> List[Dict]:
        """
        Get rooms for a specific hotel with filters.
        
        Args:
            hotel_id  : UUID of the hotel
            room_type : Optional filter by room type
            floor     : Optional filter by floor
            status    : Optional filter by status
            skip      : Number of records to skip
            limit     : Maximum number of records to return
            
        Returns:
            List of room records
        """
        try:
            params = {
                "room_type" : room_type.value if hasattr(room_type, "value") else room_type
                , "floor"   : floor
                , "status"  : status
                , "skip"    : skip
                , "limit"   : limit
            }
            
            params = {k: v for k, v in params.items() if v is not None}
            
            response = APIUtils.get(
                endpoint = f"/api/v1/room/hotel/{hotel_id}"
                , params = params
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get hotel rooms: {str(e)}")
            raise

    @staticmethod
    @tool("check_room_availability_tool")
    def check_room_availability(
        hotel_id     : UUID
        , check_in   : str
        , check_out  : str
        , room_type  : Optional[RoomType] = None
        , num_guests : int = 1
    ) -> List[Dict]:
        """
        Check available rooms for given dates.
        
        Args:
            hotel_id   : UUID of the hotel
            check_in   : Check-in date in ISO format
            check_out  : Check-out date in ISO format
            room_type  : Optional specific room type
            num_guests : Number of guests (default: 1)
            
        Returns:
            List of available rooms
        """
        try:
            params = {
                "check_in"     : check_in
                , "check_out"  : check_out
                , "room_type"  : room_type.value if hasattr(room_type, "value") else room_type
                , "num_guests" : num_guests
            }
            
            response = APIUtils.get(
                endpoint = f"/api/v1/room/hotel/{hotel_id}/available"
                , params = params
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to check room availability: {str(e)}")
            raise

    @staticmethod
    @tool("update_room_status_tool")
    def update_room_status(
        room_id  : UUID
        , status : str
    ) -> Dict:
        """
        Update room status.
        
        Args:
            room_id : UUID of the room
            status  : New room status
            
        Returns:
            Dict containing updated room information
        """
        try:
            data = {
                "status": status
            }
            
            response = APIUtils.put(
                endpoint = f"/api/v1/room/{room_id}/status"
                , data   = data
            )
            
            logger.info(
                "Room status updated"
                , extra = {
                    "room_id": str(room_id)
                    , "status": status
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to update room status: {str(e)}")
            raise

    @staticmethod
    @tool("list_all_rooms_tool")
    def get_all_rooms(
        skip  : int = 0
        , limit : int = 100
    ) -> List[Dict]:
        """
        Get all rooms in the system with pagination.
        
        Args:
            skip   : Number of records to skip
            limit  : Maximum number of records to return
            
        Returns:
            List of room records
        """
        try:
            params = {
                "skip"  : skip
                , "limit": limit
            }
            
            response = APIUtils.get(
                endpoint = "/api/v1/room/all"
                , params = params
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to list all rooms: {str(e)}")
            raise
