from uuid import UUID
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select, and_, update
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database.models.payment_model import PaymentModel
from app.database.models.booking_model import BookingModel
from app.database.schemas.payment_schema import PaymentSchemaIn, PaymentSchemaOut
from app.core.enum.enum import PaymentStatus
from loguru import logger


class PaymentService:
    
    @staticmethod
    def create_payment(
        db              : Session
        , payment_data  : PaymentSchemaIn
    ) -> PaymentSchemaOut:
        try:
            # Verify booking exists and is active
            booking = db.query(BookingModel).filter(
                and_(
                    BookingModel.id == payment_data.booking_id
                    , BookingModel.is_active == True
                )
            ).first()
            
            if not booking:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND
                    , detail    = f"Booking with id {payment_data.booking_id} not found"
                )
            
            # Verify payment amount matches booking total
            if payment_data.amount != booking.total_price:
                raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST
                    , detail    = f"Payment amount {payment_data.amount} does not match booking total {booking.total_price}"
                )
            
            db_payment = PaymentModel(
                **payment_data.model_dump()
                , payment_status = PaymentStatus.PENDING
            )
            
            db.add(db_payment)
            db.commit()
            db.refresh(db_payment)
            
            return PaymentSchemaOut.model_validate(db_payment)
        
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating payment: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = str(e)
            )
    
    @staticmethod
    def get_payment_by_id(
        db              : Session
        , payment_id    : UUID
    ) -> PaymentSchemaOut:
        try:
            stmt = select(
                PaymentModel
            ).where(
                and_(
                    PaymentModel.id == payment_id
                    , PaymentModel.is_active == True
                )
            )
            
            payment = db.execute(stmt).scalar_one_or_none()
            
            if not payment:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND
                    , detail    = f"Payment with id {payment_id} not found"
                )
            
            return PaymentSchemaOut.model_validate(payment)
        
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving payment: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to retrieve payment"
            )
    
    @staticmethod
    def get_payments_by_booking(
        db              : Session
        , booking_id    : UUID
        , skip          : int = 0
        , limit         : int = 100
    ) -> List[PaymentSchemaOut]:
        try:
            stmt = select(
                PaymentModel
            ).where(
                and_(
                    PaymentModel.booking_id == booking_id
                    , PaymentModel.is_active == True
                )
            ).offset(skip).limit(limit)
            
            payments = db.execute(stmt).scalars().all()
            
            return [PaymentSchemaOut.model_validate(payment) for payment in payments]
        
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving booking payments: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to retrieve booking payments"
            )
    
    @staticmethod
    def update_payment_status(
        db              : Session
        , payment_id    : UUID
        , status        : PaymentStatus
    ) -> PaymentSchemaOut:
        try:
            stmt = update(
                PaymentModel
            ).where(
                and_(
                    PaymentModel.id == payment_id
                    , PaymentModel.is_active == True
                )
            ).values(
                payment_status = status
                , updated_at   = datetime.now()
            ).returning(PaymentModel)
            
            result = db.execute(stmt)
            db.commit()
            
            updated_payment = result.scalar_one_or_none()
            
            if not updated_payment:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND
                    , detail    = f"Payment with id {payment_id} not found"
                )
            
            return PaymentSchemaOut.model_validate(updated_payment)
        
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error updating payment status: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to update payment status"
            )
    
    @staticmethod
    def void_payment(
        db              : Session
        , payment_id    : UUID
    ) -> bool:
        try:
            stmt = update(
                PaymentModel
            ).where(
                and_(
                    PaymentModel.id == payment_id
                    , PaymentModel.is_active == True
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
                    , detail    = f"Payment with id {payment_id} not found"
                )
            
            return True
        
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error voiding payment: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to void payment"
            )
            
    @staticmethod
    def list_payments(
        db      : Session
        , skip  : int = 0
        , limit : int = 100
    ) -> List[PaymentSchemaOut]:
        try:
            stmt = select(
                PaymentModel
            ).where(
                PaymentModel.is_active == True
            ).offset(skip).limit(limit)
            
            payments = db.execute(stmt).scalars().all()
            
            return [PaymentSchemaOut.model_validate(payment) for payment in payments]
        
        except SQLAlchemyError as e:
            logger.error(f"Database error listing payments: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to list payments"
            )