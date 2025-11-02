from uuid import UUID
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import HTTPException, status

from sqlalchemy import select, func, and_, update, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database.models.room_model import RoomModel
from app.database.models.guest_model import GuestModel
from app.database.models.booking_model import BookingModel
from app.database.models.hotel_model import HotelModel
from app.database.schemas.booking_schema import BookingSchemaIn, BookingSchemaOut

from app.services.guest_service import GuestService

from app.core.enum.enum import BookingStatus

from app import logger


class BookingService:

    @staticmethod
    def create_booking(
        db              : Session
        , booking_data  : BookingSchemaIn
    ) -> BookingSchemaOut:
        try:
            # Validate guest exists
            guest = db.query(GuestModel).filter(
                and_(
                    GuestModel.id == booking_data.guest_id
                    , GuestModel.is_active == True
                )
            ).first()
            
            if not guest:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND
                    , detail    = f"Guest with id {booking_data.guest_id} not found"
                )
                
            # Validate hotel exists
            hotel = db.query(HotelModel).filter(
                and_(
                    HotelModel.id == booking_data.hotel_id
                    , HotelModel.is_active == True
                )
            ).first()
            
            if not hotel:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND
                    , detail    = f"Hotel with id {booking_data.hotel_id} not found"
                )
                
            # Validate room exists and belongs to the hotel
            room = db.query(RoomModel).filter(
                and_(
                    RoomModel.id == booking_data.room_id
                    , RoomModel.hotel_id == booking_data.hotel_id
                    , RoomModel.is_active == True
                )
            ).first()
            
            if not room:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND
                    , detail    = f"Room with id {booking_data.room_id} not found in hotel {booking_data.hotel_id}"
                )
            
            # calculate price
            stay_duration       = (booking_data.check_out_date.date() - booking_data.check_in_date.date()).days

            logger.debug(f"Checking duration {stay_duration}")

            if not stay_duration:
                raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST
                    , detail    = "Check-out date must be at least one day after check-in date"
                )
            
            from decimal import Decimal

            total_price         = Decimal(room.price_per_night) * Decimal(stay_duration)

            booking_dicts       = booking_data.model_dump()
            db_booking          = BookingModel(
                **booking_dicts
                , total_price       = total_price
                , booking_status    = BookingStatus.PENDING
            )

            db.add(db_booking)
            db.commit()
            db.refresh(db_booking)
                
            return BookingSchemaOut.model_validate(db_booking)
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating booking: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = str(e)
            )


    
    @staticmethod
    def check_booking_by_id(
        db              : Session
        , booking_id    : UUID
    ) -> BookingSchemaOut:
        
        try:

            stmt    = select(
                BookingModel
            ).where(
                and_(
                    BookingModel.id == booking_id
                    , BookingModel.is_active == True
                )
            )

            booking = db.execute(stmt).scalar_one_or_none()

            if not booking:
                logger.warning(f"Booking with id {booking_id} not found")
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND
                    , detail    = f"Booking with id {booking_id} not found"
                )
            
            
            return BookingSchemaOut.model_validate(booking)
        
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving booking: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve booking"
            )

    @staticmethod
    def list_all_bookings(
        db      : Session
        , skip  : int = 0
        , limit : int = 100
    ) -> List[BookingSchemaOut]:
        
        try:

            stmt    = select(
                BookingModel
            ).where(
                BookingModel.is_active == True
            ).offset(skip).limit(limit)

            bookings    = db.execute(stmt).scalars().all()

            return [BookingSchemaOut.model_validate(booking) for booking in bookings]


        except SQLAlchemyError as e:
            logger.error(f"Database error listing bookings: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list bookings"
            )
        

    @staticmethod
    def update_booking_by_id(
        db              : Session
        , booking_id    : UUID
        , booking_data  : BookingSchemaIn
    ) -> BookingSchemaOut:
        
        try:

            booking = BookingService.check_booking_by_id(booking_id)

            update_data = booking_data.model_dump()

            stmt    = update(
                BookingModel
            ).where(
                and_(
                    BookingModel.id == booking_id
                    , BookingModel.is_active    == True
                )
            ).values(
                **update_data
                , updated_at    = datetime.now()
            ).returning(BookingModel)


            result  = db.execute(stmt)

            db.commit()

            updated_booking  = result.scalar_one_or_none()

            return BookingSchemaOut.model_validate(updated_booking)
        
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error updating booking: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update booking"
            )
        

    @staticmethod
    def cancel_booking_by_id(
        db              : Session
        , guest_id      : UUID
    ) -> bool:
        try:
            query       = db.query(
                BookingModel
            ).filter(
                and_(
                    BookingModel.guest_id   == True
                    , BookingModel.is_active    == True
                )
            )

            booking     = query.first()

            if not booking:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND
                    , detail    = f"No active booking found for guest {guest_id}"
                )

            booking.is_active   = False
            booking.deleted_at  = datetime.now()
            db.commit()
            
            return True
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error deleting booking: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail      = "Failed to delete booking"
            )
        
    @staticmethod
    def cancel_booking_by_guest_id(
        db          : Session,
        guest_id    : UUID
    ) -> bool:
        try:
            stmt = update(BookingModel).where(
                and_(
                    BookingModel.guest_id == guest_id,
                    BookingModel.is_active == True,
                    BookingModel.booking_status != BookingStatus.CANCELLED
                )
            ).values(
                booking_status = BookingStatus.CANCELLED,
                updated_at = datetime.utcnow()
            )

            result = db.execute(stmt)
            db.commit()

            return result.rowcount > 0

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error canceling booking: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to cancel booking"
            )

            



    @staticmethod
    def all_booking_by_guest_id(
        db          : Session
        , guest_id  : UUID
        , skip      : int = 0
        , limit     : int = 100
    ) -> List[Dict]:
        
        try:


            stmt    = select(
                BookingModel.id
                , BookingModel.check_in_date
                , BookingModel.check_out_date
                , BookingModel.total_price
                , BookingModel.booking_status
                , BookingModel.num_guests
                , GuestModel.first_name
                , GuestModel.last_name
                , GuestModel.email
                , GuestModel.phone_number
            ).join(
                GuestModel, BookingModel.guest_id == GuestModel.id
            ).where(
                and_(
                    GuestModel.id == guest_id
                    , GuestModel.is_active == True
                    , BookingModel.is_active == True
                )
            ).offset(skip).limit(limit)

            results = db.execute(stmt).all()

            return [{
                "booking_id"        : row.id
                , "guest_info"      : {
                    "first_name"    : row.first_name
                    , "last_name"   : row.last_name
                    , "email"       : row.email
                    , "phone_number": row.phone_number
                },
                "booking_details": {
                    "check_in_date"     : row.check_in_date
                    , "check_out_date"  : row.check_out_date
                    , "total_price"     : str(row.total_price)
                    , "booking_status"  : row.booking_status
                    , "num_guests"      : row.num_guests
                }
            } for row in results]
        
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving guest bookings: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail      = "Failed to retrieve guest bookings"
            )
        
    @staticmethod
    def check_room_availability(
        db                : Session
        , room_id         : UUID
        , check_in_date   : datetime
        , check_out_date  : datetime
    ) -> bool:
        try:
            existing_booking = db.query(BookingModel).filter(
                BookingModel.room_id == room_id,
                BookingModel.is_active == True,
                BookingModel.booking_status != BookingStatus.CANCELLED,
                or_(
                    and_(
                        BookingModel.check_in_date <= check_in_date,
                        BookingModel.check_out_date > check_in_date
                    ),
                    and_(
                        BookingModel.check_in_date < check_out_date,
                        BookingModel.check_out_date >= check_out_date
                    )
                )
            ).first()
            
            return existing_booking is None
            
        except SQLAlchemyError as e:
            logger.error(f"Error checking room availability: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail      = "Failed to check room availability"
            )
        

    
    @staticmethod
    def get_booking_info(
        db          : Session
        , guest_id  : UUID
    ) -> Dict:
        
        try:

            # check guest 
            db_guest   = GuestService.get_guest_by_id(db, guest_id)

            if not db_guest:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND
                    , detail    = f"Guest with guest_id not found"
                )
            
            # getting the booknig info

            booking_query   = (
                db.query(
                    BookingModel
                    , HotelModel.name.label("hotel_name")
                    , HotelModel.address.label("hotel_address")
                    , RoomModel.room_number
                    , RoomModel.room_type
                    , RoomModel.price_per_night
                )
                .join(RoomModel, BookingModel.room_id == RoomModel.id)
                .join(HotelModel, BookingModel.hotel_id == HotelModel.id)
                .filter(
                    and_(
                        BookingModel.guest_id   == guest_id
                        , BookingModel.is_active    == True
                    )
                )
                .order_by(
                    BookingModel.check_out_date.desc()
                )
            )

            bookings        = booking_query.all()

            result          = []

            for booking_data in bookings:
                booking     = booking_data[0]

                booking_info = {
                    "booking_id"        : str(booking.id),
                    "hotel_name"        : booking_data.hotel_name,
                    "hotel_address"     : booking_data.hotel_address,
                    "room_number"       : booking_data.room_number,
                    "room_type"         : booking_data.room_type,
                    "check_in_date"     : booking.check_in_date.date().isoformat(),
                    "check_out_date"    : booking.check_out_date.date().isoformat(),
                    "stay_duration"     : (booking.check_out_date.date() - booking.check_in_date.date()).days,
                    "price_per_night"   : float(booking_data.price_per_night),
                    "total_price"       : float(booking.total_price),
                    "booking_status"    : booking.booking_status,
                    "num_guests"        : booking.num_guests,
                    "created_at"        : booking.created_at.isoformat(),
                    "special_requests"  : booking.special_requests
                }

                result.append(booking_info)

            return {
            "guest_id"          : str(guest_id),
                "guest_name"    : f"{db_guest.first_name} {db_guest.last_name}",
                "total_bookings": len(result),
                "bookings"      : result
            }

        except SQLAlchemyError as e:
            logger.error(f"Error checking booking info: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail      = "Error checking booking info"
            )