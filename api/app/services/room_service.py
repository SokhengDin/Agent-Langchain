from uuid import UUID
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select, and_, or_, update
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database.models.room_model import RoomModel
from app.database.models.hotel_model import HotelModel
from app.database.models.booking_model import BookingModel
from app.database.schemas.room_schema import RoomSchemaIn, RoomSchemaOut
from app.core.enum.enum import RoomType, BookingStatus
from loguru import logger

class RoomService:
    
    @staticmethod
    def create_room(
        db             : Session
        , room_data    : RoomSchemaIn
    ) -> RoomSchemaOut:
        try:
            # Verify hotel exists
            hotel = db.query(HotelModel).filter(
                and_(
                    HotelModel.id == room_data.hotel_id
                    , HotelModel.is_active == True
                )
            ).first()
            
            if not hotel:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND
                    , detail    = f"Hotel with id {room_data.hotel_id} not found"
                )
            
            # Check for duplicate room number in the same hotel
            existing_room = db.query(RoomModel).filter(
                and_(
                    RoomModel.hotel_id == room_data.hotel_id
                    , RoomModel.room_number == room_data.room_number
                    , RoomModel.is_active == True
                )
            ).first()
            
            if existing_room:
                raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST
                    , detail    = f"Room number {room_data.room_number} already exists in this hotel"
                )
            
            db_room = RoomModel(**room_data.model_dump())
            
            db.add(db_room)
            db.commit()
            db.refresh(db_room)
            
            return RoomSchemaOut.model_validate(db_room)
        
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating room: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = str(e)
            )
    
    @staticmethod
    def get_room_by_id(
        db          : Session
        , room_id   : UUID
    ) -> RoomSchemaOut:
        try:
            stmt = select(
                RoomModel
            ).where(
                and_(
                    RoomModel.id == room_id
                    , RoomModel.is_active == True
                )
            )
            
            room = db.execute(stmt).scalar_one_or_none()
            
            if not room:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND
                    , detail    = f"Room with id {room_id} not found"
                )
            
            return RoomSchemaOut.model_validate(room)
        
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving room: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to retrieve room"
            )
    
    @staticmethod
    def get_rooms_by_hotel(
        db          : Session
        , hotel_id  : UUID
        , room_type : Optional[RoomType] = None
        , floor     : Optional[int] = None
        , status    : Optional[str] = None
        , skip      : int = 0
        , limit     : int = 100
    ) -> List[RoomSchemaOut]:
        try:
            query = select(RoomModel).where(
                and_(
                    RoomModel.hotel_id == hotel_id
                    , RoomModel.is_active == True
                )
            )
            
            if room_type:
                query = query.where(RoomModel.room_type == room_type)
                
            if floor:
                query = query.where(RoomModel.floor == floor)
                
            if status:
                query = query.where(RoomModel.status == status)
            
            query = query.offset(skip).limit(limit)
            
            rooms = db.execute(query).scalars().all()
            
            return [RoomSchemaOut.model_validate(room) for room in rooms]
        
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving hotel rooms: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to retrieve hotel rooms"
            )
    
    @staticmethod
    def update_room(
        db           : Session
        , room_id    : UUID
        , room_data  : RoomSchemaIn
    ) -> RoomSchemaOut:
        try:
            # Verify room exists
            existing_room = RoomService.get_room_by_id(db, room_id)
            
            # Check for room number conflict if it's being changed
            if room_data.room_number != existing_room.room_number:
                room_conflict = db.query(RoomModel).filter(
                    and_(
                        RoomModel.hotel_id == room_data.hotel_id
                        , RoomModel.room_number == room_data.room_number
                        , RoomModel.id != room_id
                        , RoomModel.is_active == True
                    )
                ).first()
                
                if room_conflict:
                    raise HTTPException(
                        status_code = status.HTTP_400_BAD_REQUEST
                        , detail    = f"Room number {room_data.room_number} already exists in this hotel"
                    )
            
            update_data = room_data.model_dump()
            
            stmt = update(
                RoomModel
            ).where(
                and_(
                    RoomModel.id == room_id
                    , RoomModel.is_active == True
                )
            ).values(
                **update_data
                , updated_at = datetime.now()
            ).returning(RoomModel)
            
            result = db.execute(stmt)
            db.commit()
            
            updated_room = result.scalar_one_or_none()
            
            return RoomSchemaOut.model_validate(updated_room)
        
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error updating room: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to update room"
            )
    
    @staticmethod
    def delete_room(
        db          : Session
        , room_id   : UUID
    ) -> bool:
        try:
            stmt = update(
                RoomModel
            ).where(
                and_(
                    RoomModel.id == room_id
                    , RoomModel.is_active == True
                )
            ).values(
                is_active    = False
                , deleted_at = datetime.now()
            )
            
            result = db.execute(stmt)
            db.commit()
            
            if result.rowcount == 0:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND
                    , detail    = f"Room with id {room_id} not found"
                )
            
            return True
        
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error deleting room: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to delete room"
            )
        
    @staticmethod
    def get_all_rooms(
        db          : Session
        , skip      : int = 0
        , limit     : int = 100
    ) -> List[RoomSchemaOut]:
        """Get all active rooms with pagination"""
        try:
            stmt    = select(
                RoomModel
            ).where(
                RoomModel.is_active == True
            ).offset(
                skip
            ).limit(
                limit
            )

            rooms   = db.execute(stmt).scalars().all()

            return [RoomSchemaOut.model_validate(room) for room in rooms]

        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving all rooms: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to retrieve rooms"
            )

    @staticmethod
    def get_available_rooms(
        db          : Session
        , hotel_id  : UUID
        , check_in  : datetime
        , check_out : datetime
        , room_type : Optional[RoomType] = None
        , num_guests: Optional[int] = None
        , skip      : int = 0
        , limit     : int = 100
    ) -> List[RoomSchemaOut]:
        """Get available rooms for a hotel based on check-in/out dates and optional filters"""
        try:
            # Verify hotel exists
            hotel = db.query(HotelModel).filter(
                and_(
                    HotelModel.id == hotel_id,
                    HotelModel.is_active == True
                )
            ).first()

            if not hotel:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND,
                    detail      = f"Hotel with id {hotel_id} not found"
                )

            # Subquery to find rooms that are booked during the requested dates
            booked_room_ids = select(BookingModel.room_id).where(
                and_(
                    BookingModel.hotel_id == hotel_id,
                    BookingModel.is_active == True,
                    BookingModel.booking_status.in_([
                        BookingStatus.CONFIRMED,
                        BookingStatus.CHECKED_IN,
                        BookingStatus.PENDING
                    ]),
                    # Check for date overlap: booking overlaps if it starts before check_out and ends after check_in
                    BookingModel.check_in_date < check_out,
                    BookingModel.check_out_date > check_in
                )
            )

            # Query for available rooms (not in booked rooms)
            query = select(RoomModel).where(
                and_(
                    RoomModel.hotel_id == hotel_id,
                    RoomModel.is_active == True,
                    RoomModel.id.not_in(booked_room_ids)
                )
            )

            # Apply optional filters
            if room_type:
                query = query.where(RoomModel.room_type == room_type)

            if num_guests:
                query = query.where(RoomModel.max_occupancy >= num_guests)

            query = query.offset(skip).limit(limit)

            rooms = db.execute(query).scalars().all()

            return [RoomSchemaOut.model_validate(room) for room in rooms]

        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving available rooms: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail      = "Failed to retrieve available rooms"
            )