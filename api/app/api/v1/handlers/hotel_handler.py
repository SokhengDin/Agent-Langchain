from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session

from app.services.hotel_service import HotelService
from app.database.schemas.hotel_schema import HotelSchemaIn, HotelSchemaOut
from app.database.schemas.room_schema import RoomSchemaOut
from app.database import get_db
from loguru import logger

router = APIRouter()


@router.post(
    "/"
    , response_model  = HotelSchemaOut
    , status_code    = status.HTTP_201_CREATED
)
def create_hotel(
    hotel_data   : HotelSchemaIn
    , db         : Session = Depends(get_db)
) -> HotelSchemaOut:
    logger.info("Creating new hotel")
    
    hotel = HotelService.create_hotel(
        db          = db
        , hotel_data = hotel_data
    )
    
    logger.info(
        "Hotel created successfully"
        , extra = {"hotel_id": str(hotel.id)}
    )
    
    return hotel

@router.get(
    "/search"
    , response_model = List[HotelSchemaOut]
)
def search_hotels(
    search_term    : Optional[str] = None
    , min_rating   : Optional[Decimal] = None
    , city         : Optional[str] = None
    , skip         : int = 0
    , limit        : int = 100
    , db           : Session = Depends(get_db)
) -> List[HotelSchemaOut]:
    return HotelService.search_hotels(
        db            = db
        , search_term = search_term
        , min_rating  = min_rating
        , city        = city
        , skip        = skip
        , limit       = limit
    )

@router.get(
    "/{hotel_id}"
    , response_model = HotelSchemaOut
)
def get_hotel(
    hotel_id    : UUID
    , db        : Session = Depends(get_db)
) -> HotelSchemaOut:
    return HotelService.get_hotel_by_id(
        db          = db
        , hotel_id  = hotel_id
    )


@router.get(
    "/"
    , response_model = List[HotelSchemaOut]
)
def list_hotels(
    skip     : int = 0
    , limit  : int = 100
    , db     : Session = Depends(get_db)
) -> List[HotelSchemaOut]:
    return HotelService.list_hotels(
        db      = db
        , skip  = skip
        , limit = limit
    )


@router.put(
    "/{hotel_id}"
    , response_model = HotelSchemaOut
)
def update_hotel(
    hotel_id     : UUID
    , hotel_data : HotelSchemaIn
    , db         : Session = Depends(get_db)
) -> HotelSchemaOut:
    logger.info(f"Updating hotel: {hotel_id}")
    
    hotel = HotelService.update_hotel(
        db          = db
        , hotel_id  = hotel_id
        , hotel_data = hotel_data
    )
    
    logger.info(
        "Hotel updated successfully"
        , extra = {"hotel_id": str(hotel_id)}
    )
    
    return hotel


@router.delete(
    "/{hotel_id}"
    , status_code = status.HTTP_204_NO_CONTENT
)
def delete_hotel(
    hotel_id    : UUID
    , db        : Session = Depends(get_db)
):
    logger.info(f"Deleting hotel: {hotel_id}")
    
    HotelService.delete_hotel(
        db          = db
        , hotel_id  = hotel_id
    )
    
    logger.info(f"Hotel deleted: {hotel_id}")



@router.get(
    "/{hotel_id}/rooms"
    , response_model = List[RoomSchemaOut]
)
def get_hotel_rooms(
    hotel_id    : UUID
    , skip      : int = 0
    , limit     : int = 100
    , db        : Session = Depends(get_db)
) -> List[RoomSchemaOut]:
    return HotelService.get_hotel_rooms(
        db          = db
        , hotel_id  = hotel_id
        , skip      = skip
        , limit     = limit
    )