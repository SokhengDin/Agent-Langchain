from uuid import UUID
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select, and_, or_, update
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database.models.guest_model import GuestModel
from app.database.schemas.guest_schema import GuestSchemaIn, GuestSchemaOut
from app import logger


class GuestService:
    
    @staticmethod
    def create_guest(
        db              : Session
        , guest_data    : GuestSchemaIn
    ) -> GuestSchemaOut:
        try:
            # Check if guet with same email already exists
            existing_guest = db.query(GuestModel).filter(
                and_(
                    GuestModel.email == guest_data.email
                    , GuestModel.is_active == True
                )
            ).first()
            
            if existing_guest:
                raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST
                    , detail    = f"Guest with email {guest_data.email} already exists"
                )
            
            db_guest = GuestModel(**guest_data.model_dump())
            
            db.add(db_guest)
            db.commit()
            db.refresh(db_guest)
            
            return GuestSchemaOut.model_validate(db_guest)
        
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating guest: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = str(e)
            )
    
    @staticmethod
    def get_guest_by_id(
        db          : Session
        , guest_id  : UUID
    ) -> GuestSchemaOut:
        try:
            stmt = select(
                GuestModel
            ).where(
                and_(
                    GuestModel.id == guest_id
                    , GuestModel.is_active == True
                )
            )
            
            guest = db.execute(stmt).scalar_one_or_none()
            
            if not guest:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND
                    , detail    = f"Guest with id {guest_id} not found"
                )
            
            return GuestSchemaOut.model_validate(guest)
        
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving guest: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to retrieve guest"
            )
    
    @staticmethod
    def get_guest_by_email(
        db          : Session
        , email     : str
    ) -> GuestSchemaOut:
        try:
            stmt = select(
                GuestModel
            ).where(
                and_(
                    GuestModel.email == email
                    , GuestModel.is_active == True
                )
            )
            
            guest = db.execute(stmt).scalar_one_or_none()
            
            if not guest:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND
                    , detail    = f"Guest with email {email} not found"
                )
            
            return GuestSchemaOut.model_validate(guest)
        
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving guest by email: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to retrieve guest"
            )
    
    @staticmethod
    def list_all_guests(
        db      : Session
        , skip  : int = 0
        , limit : int = 100
    ) -> List[GuestSchemaOut]:
        try:
            stmt = select(
                GuestModel
            ).where(
                GuestModel.is_active == True
            ).offset(skip).limit(limit)
            
            guests = db.execute(stmt).scalars().all()
            
            return [GuestSchemaOut.model_validate(guest) for guest in guests]
        
        except SQLAlchemyError as e:
            logger.error(f"Database error listing guests: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to list guests"
            )
    
    @staticmethod
    def update_guest(
        db              : Session
        , guest_id      : UUID
        , guest_data    : GuestSchemaIn
    ) -> GuestSchemaOut:
        try:
            # Check if guest exists
            existing_guest = GuestService.get_guest_by_id(db, guest_id)
            
            # Check if email is being updated
            if guest_data.email != existing_guest.email:
                email_taken = db.query(GuestModel).filter(
                    and_(
                        GuestModel.email == guest_data.email
                        , GuestModel.id != guest_id
                        , GuestModel.is_active == True
                    )
                ).first()
                
                if email_taken:
                    raise HTTPException(
                        status_code = status.HTTP_400_BAD_REQUEST
                        , detail    = f"Email {guest_data.email} is already taken"
                    )
            
            update_data = guest_data.model_dump()
            
            stmt = update(
                GuestModel
            ).where(
                and_(
                    GuestModel.id == guest_id
                    , GuestModel.is_active == True
                )
            ).values(
                **update_data
                , updated_at = datetime.now()
            ).returning(GuestModel)
            
            result = db.execute(stmt)
            db.commit()
            
            updated_guest = result.scalar_one_or_none()
            
            return GuestSchemaOut.model_validate(updated_guest)
        
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error updating guest: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to update guest"
            )
    
    @staticmethod
    def delete_guest(
        db          : Session
        , guest_id  : UUID
    ) -> bool:
        try:
            # Check if guest exists
            existing_guest = GuestService.get_guest_by_id(db, guest_id)
            
            stmt = update(
                GuestModel
            ).where(
                and_(
                    GuestModel.id == guest_id
                    , GuestModel.is_active == True
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
                    , detail    = f"Guest with id {guest_id} not found"
                )
            
            return True
        
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error deleting guest: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to delete guest"
            )
    
    @staticmethod
    def search_guests(
        db              : Session
        , search_term   : str
        , skip          : int = 0
        , limit         : int = 100
    ) -> List[GuestSchemaOut]:
        try:
            stmt = select(
                GuestModel
            ).where(
                and_(
                    GuestModel.is_active == True
                    , or_(
                        GuestModel.first_name.ilike(f"%{search_term}%")
                        , GuestModel.last_name.ilike(f"%{search_term}%")
                        , GuestModel.email.ilike(f"%{search_term}%")
                        , GuestModel.phone_number.ilike(f"%{search_term}%")
                    )
                )
            ).offset(skip).limit(limit)
            
            guests = db.execute(stmt).scalars().all()
            
            return [GuestSchemaOut.model_validate(guest) for guest in guests]
        
        except SQLAlchemyError as e:
            logger.error(f"Database error searching guests: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to search guests"
            )