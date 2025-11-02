from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
from uuid import UUID
from sqlalchemy.orm import Session

from app.services.booking_service import BookingService
from app.database.schemas.booking_schema import BookingSchemaIn, BookingSchemaOut
from app.database import get_db
from app import logger

router = APIRouter()

@router.post(
    ""
    , response_model    = BookingSchemaOut
    , status_code       = status.HTTP_201_CREATED
)
def create_booking(
    booking_data    : BookingSchemaIn,
    db              : Session = Depends(get_db)
) -> BookingSchemaOut:
    logger.info("Creating booking")
    
    booking = BookingService.create_booking(
        db           = db,
        booking_data = booking_data
    )
    
    logger.info(
        "Booking created",
        extra={"booking_id": str(booking.id)}
    )
    
    return booking

@router.get(
    "/guest/{guest_id}/bookings"
    , response_model = List[Dict]
)
def get_guest_bookings(
    guest_id    : UUID,
    skip        : int = 0,
    limit       : int = 100,
    db          : Session = Depends(get_db)
) -> List[Dict]:
    return BookingService.all_booking_by_guest_id(
        db       = db,
        guest_id = guest_id,
        skip     = skip,
        limit    = limit
    )

@router.post(
    "/guest/{guest_id}/cancel"
    , response_model = bool
)
def cancel_guest_booking(
    guest_id    : UUID,
    db          : Session = Depends(get_db)
) -> bool:
    logger.info(f"Cancelling booking for guest: {guest_id}")
    
    result = BookingService.cancel_booking_by_guest_id(
        db       = db,
        guest_id = guest_id
    )
    
    if result:
        logger.info(f"Successfully cancelled booking for guest: {guest_id}")
    else:
        logger.warning(f"No active bookings found for guest: {guest_id}")
    
    return result


@router.get(
    "/"
    , response_model = List[BookingSchemaOut]
)
def list_bookings(
    skip     : int = 0,
    limit    : int = 100,
    db       : Session = Depends(get_db)
) -> List[BookingSchemaOut]:
    return BookingService.list_all_bookings(
        db    = db,
        skip  = skip,
        limit = limit
    )

@router.get("/{guest_id}", response_model=Dict)
def get_guest_info(
    guest_id    : UUID
    , db        : Session   = Depends(get_db)
) -> Dict:
    
    return BookingService.get_booking_info(db, guest_id)