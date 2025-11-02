from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from app.services.payment_service import PaymentService
from app.database.schemas.payment_schema import PaymentSchemaIn, PaymentSchemaOut
from app.core.enum.enum import PaymentStatus
from app.database import get_db
from loguru import logger

router = APIRouter()


@router.post(
    ""
    , response_model  = PaymentSchemaOut
    , status_code    = status.HTTP_201_CREATED
)
def create_payment(
    payment_data : PaymentSchemaIn
    , db         : Session = Depends(get_db)
) -> PaymentSchemaOut:
    logger.info("Creating new payment")
    
    payment = PaymentService.create_payment(
        db            = db
        , payment_data = payment_data
    )
    
    logger.info(
        "Payment created successfully"
        , extra = {
            "payment_id" : str(payment.id)
            , "booking_id": str(payment.booking_id)
        }
    )
    
    return payment


@router.get(
    "/{payment_id}"
    , response_model = PaymentSchemaOut
)
def get_payment(
    payment_id   : UUID
    , db         : Session = Depends(get_db)
) -> PaymentSchemaOut:
    return PaymentService.get_payment_by_id(
        db            = db
        , payment_id  = payment_id
    )


@router.get(
    "/booking/{booking_id}"
    , response_model = List[PaymentSchemaOut]
)
def get_booking_payments(
    booking_id   : UUID
    , skip       : int = 0
    , limit      : int = 100
    , db         : Session = Depends(get_db)
) -> List[PaymentSchemaOut]:
    return PaymentService.get_payments_by_booking(
        db            = db
        , booking_id  = booking_id
        , skip        = skip
        , limit       = limit
    )


@router.put(
    "/{payment_id}/status"
    , response_model = PaymentSchemaOut
)
def update_payment_status(
    payment_id   : UUID
    , status     : PaymentStatus
    , db         : Session = Depends(get_db)
) -> PaymentSchemaOut:
    logger.info(f"Updating payment status: {payment_id} to {status}")
    
    payment = PaymentService.update_payment_status(
        db            = db
        , payment_id  = payment_id
        , status      = status
    )
    
    logger.info(
        "Payment status updated successfully"
        , extra = {
            "payment_id" : str(payment_id)
            , "new_status": status
        }
    )
    
    return payment


@router.delete(
    "/{payment_id}"
    , status_code = status.HTTP_204_NO_CONTENT
)
def void_payment(
    payment_id   : UUID
    , db         : Session = Depends(get_db)
):
    logger.info(f"Voiding payment: {payment_id}")
    
    PaymentService.void_payment(
        db            = db
        , payment_id  = payment_id
    )
    
    logger.info(f"Payment voided: {payment_id}")


@router.get(
    "/"
    , response_model = List[PaymentSchemaOut]
)
def list_payments(
    skip     : int = 0
    , limit  : int = 100
    , db     : Session = Depends(get_db)
) -> List[PaymentSchemaOut]:
    return PaymentService.list_payments(
        db      = db
        , skip  = skip
        , limit = limit
    )