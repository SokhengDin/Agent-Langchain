from uuid import UUID
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select, and_, or_, update
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database.models.hotel_model import HotelModel
from app.database.models.room_model import RoomModel
from app.database.schemas.hotel_schema import HotelSchemaIn, HotelSchemaOut
from loguru import logger


class HotelService:
    
    @staticmethod
    def create_hotel(
        db              : Session
        , hotel_data    : HotelSchemaIn
    ) -> HotelSchemaOut:
        try:
            # Check if hotel with same name and address exists
            existing_hotel = db.query(HotelModel).filter(
                and_(
                    HotelModel.name == hotel_data.name
                    , HotelModel.address == hotel_data.address
                    , HotelModel.is_active == True
                )
            ).first()
            
            if existing_hotel:
                raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST
                    , detail    = f"Hotel with name {hotel_data.name} at this address already exists"
                )
            
            db_hotel = HotelModel(**hotel_data.model_dump())
            
            db.add(db_hotel)
            db.commit()
            db.refresh(db_hotel)
            
            return HotelSchemaOut.model_validate(db_hotel)
        
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating hotel: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = str(e)
            )
    
    @staticmethod
    def get_hotel_by_id(
        db          : Session
        , hotel_id  : UUID
    ) -> HotelSchemaOut:
        try:
            stmt = select(
                HotelModel
            ).where(
                and_(
                    HotelModel.id == hotel_id
                    , HotelModel.is_active == True
                )
            )
            
            hotel = db.execute(stmt).scalar_one_or_none()
            
            if not hotel:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND
                    , detail    = f"Hotel with id {hotel_id} not found"
                )
            
            return HotelSchemaOut.model_validate(hotel)
        
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving hotel: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to retrieve hotel"
            )
    
    @staticmethod
    def list_hotels(
        db      : Session
        , skip  : int = 0
        , limit : int = 100
    ) -> List[HotelSchemaOut]:
        try:
            stmt = select(
                HotelModel
            ).where(
                HotelModel.is_active == True
            ).offset(skip).limit(limit)
            
            hotels = db.execute(stmt).scalars().all()
            
            return [HotelSchemaOut.model_validate(hotel) for hotel in hotels]
        
        except SQLAlchemyError as e:
            logger.error(f"Database error listing hotels: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to list hotels"
            )
    
    @staticmethod
    def update_hotel(
        db              : Session
        , hotel_id      : UUID
        , hotel_data    : HotelSchemaIn
    ) -> HotelSchemaOut:
        try:
            # Check if hotel exists
            existing_hotel  = HotelService.get_hotel_by_id(db, hotel_id)
            
            update_data     = hotel_data.model_dump()
            
            stmt = update(
                HotelModel
            ).where(
                and_(
                    HotelModel.id == hotel_id
                    , HotelModel.is_active == True
                )
            ).values(
                **update_data
                , updated_at = datetime.now()
            ).returning(HotelModel)
            
            result = db.execute(stmt)
            db.commit()
            
            updated_hotel = result.scalar_one_or_none()
            
            return HotelSchemaOut.model_validate(updated_hotel)
        
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error updating hotel: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to update hotel"
            )
    
    @staticmethod
    def delete_hotel(
        db          : Session
        , hotel_id  : UUID
    ) -> bool:
        try:
            # Check if hotel exists
            existing_hotel = HotelService.get_hotel_by_id(db, hotel_id)
            
            stmt = update(
                HotelModel
            ).where(
                and_(
                    HotelModel.id == hotel_id
                    , HotelModel.is_active == True
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
                    , detail    = f"Hotel with id {hotel_id} not found"
                )
            
            return True
        
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error deleting hotel: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to delete hotel"
            )
    
    @staticmethod
    def search_hotels(
        db              : Session
        , search_term   : str
        , min_rating    : Optional[Decimal] = None
        , city          : Optional[str] = None
        , skip          : int = 0
        , limit         : int = 100
    ) -> List[HotelSchemaOut]:
        try:
            query = select(HotelModel).where(HotelModel.is_active == True)
            
            if search_term:
                query = query.where(
                    or_(
                        HotelModel.name.ilike(f"%{search_term}%")
                        , HotelModel.city.ilike(f"%{search_term}%")
                        , HotelModel.address.ilike(f"%{search_term}%")
                        , HotelModel.description.ilike(f"%{search_term}%")
                        , HotelModel.description.ilike(f"%{search_term}%")
                    )
                )
            
            if min_rating:
                query = query.where(HotelModel.star_rating >= min_rating)
                
            if city:
                query = query.where(HotelModel.city.ilike(f"%{city}%"))
                
            query = query.offset(skip).limit(limit)
            
            hotels = db.execute(query).scalars().all()
            
            return [HotelSchemaOut.model_validate(hotel) for hotel in hotels]
            
        except SQLAlchemyError as e:
            logger.error(f"Database error searching hotels: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to search hotels"
            )
            
    @staticmethod
    def get_hotel_rooms(
        db          : Session
        , hotel_id  : UUID
        , skip      : int = 0
        , limit     : int = 100
    ) -> List[RoomModel]:
        try:
            # Verify hotel exists
            HotelService.get_hotel_by_id(db, hotel_id)
            
            stmt = select(
                RoomModel
            ).where(
                and_(
                    RoomModel.hotel_id == hotel_id
                    , RoomModel.is_active == True
                )
            ).offset(skip).limit(limit)
            
            rooms = db.execute(stmt).scalars().all()
            
            return rooms
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving hotel rooms: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to retrieve hotel rooms"
            )