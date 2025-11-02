from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Session

from app.services.room_service import RoomService
from app.database.schemas.room_schema import RoomSchemaIn, RoomSchemaOut
from app.core.enum.enum import RoomType
from app.database import get_db
from loguru import logger

router = APIRouter()


@router.post(
    ""
    , response_model  = RoomSchemaOut
    , status_code    = status.HTTP_201_CREATED
)
def create_room(
    room_data    : RoomSchemaIn
    , db         : Session = Depends(get_db)
) -> RoomSchemaOut:
    logger.info("Creating new room")
    
    room = RoomService.create_room(
        db          = db
        , room_data = room_data
    )
    
    logger.info(
        "Room created successfully"
        , extra = {
            "room_id"   : str(room.id)
            , "hotel_id": str(room.hotel_id)
        }
    )
    
    return room

@router.get(
    "/all"
    , response_model = List[RoomSchemaOut]
)
def get_all_rooms(
    skip    : int = 0
    , limit   : int = 100
    , db      : Session = Depends(get_db)
) -> List[RoomSchemaOut]:
    return RoomService.get_all_rooms(
        db          = db
        , skip      = skip
        , limit     = limit
    )


@router.get(
    "/{room_id}"
    , response_model = RoomSchemaOut
)
def get_room(
    room_id     : UUID
    , db        : Session = Depends(get_db)
) -> RoomSchemaOut:
    return RoomService.get_room_by_id(
        db        = db
        , room_id = room_id
    )


@router.get(
    "/hotel/{hotel_id}/available"
    , response_model = List[RoomSchemaOut]
)
def get_available_rooms(
    hotel_id    : UUID
    , check_in  : date = Query(..., description="Check-in date (YYYY-MM-DD)")
    , check_out : date = Query(..., description="Check-out date (YYYY-MM-DD)")
    , room_type : Optional[RoomType] = Query(None, description="Filter by room type")
    , num_guests: Optional[int] = Query(None, description="Number of guests")
    , skip      : int = 0
    , limit     : int = 100
    , db        : Session = Depends(get_db)
) -> List[RoomSchemaOut]:
    """Get available rooms for a hotel based on check-in/out dates"""
    logger.info(f"Checking available rooms for hotel {hotel_id} from {check_in} to {check_out}")

    # Convert date to datetime for database comparison
    from datetime import datetime, time
    check_in_dt = datetime.combine(check_in, time.min)
    check_out_dt = datetime.combine(check_out, time.min)

    return RoomService.get_available_rooms(
        db          = db
        , hotel_id  = hotel_id
        , check_in  = check_in_dt
        , check_out = check_out_dt
        , room_type = room_type
        , num_guests= num_guests
        , skip      = skip
        , limit     = limit
    )


@router.get(
    "/hotel/{hotel_id}"
    , response_model = List[RoomSchemaOut]
)
def get_hotel_rooms(
    hotel_id    : UUID
    , room_type : Optional[RoomType] = None
    , floor     : Optional[int] = None
    , status    : Optional[str] = None
    , skip      : int = 0
    , limit     : int = 100
    , db        : Session = Depends(get_db)
) -> List[RoomSchemaOut]:
    return RoomService.get_rooms_by_hotel(
        db          = db
        , hotel_id  = hotel_id
        , room_type = room_type
        , floor     = floor
        , status    = status
        , skip      = skip
        , limit     = limit
    )


@router.put(
    "/{room_id}"
    , response_model = RoomSchemaOut
)
def update_room(
    room_id     : UUID
    , room_data : RoomSchemaIn
    , db        : Session = Depends(get_db)
) -> RoomSchemaOut:
    logger.info(f"Updating room: {room_id}")
    
    room = RoomService.update_room(
        db          = db
        , room_id   = room_id
        , room_data = room_data
    )
    
    logger.info(
        "Room updated successfully"
        , extra = {
            "room_id"   : str(room_id)
            , "hotel_id": str(room.hotel_id)
        }
    )
    
    return room


@router.delete(
    "/{room_id}"
    , status_code = status.HTTP_204_NO_CONTENT
)
def delete_room(
    room_id     : UUID
    , db        : Session = Depends(get_db)
):
    logger.info(f"Deleting room: {room_id}")
    
    RoomService.delete_room(
        db        = db
        , room_id = room_id
    )
    
    logger.info(f"Room deleted: {room_id}")