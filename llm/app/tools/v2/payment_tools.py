from typing import Dict, List, Optional
from uuid import UUID
from decimal import Decimal
from datetime import datetime

from langchain_core.tools import tool

from app.schema.payment_schema import PaymentSchemaIn
from app.core.utils.api_utils_sync import APIUtils
from app.core.enum.enum import PaymentStatus

from app import logger


class PaymentTools:
    """Tools for managing payment operations in the hotel system"""
    
    @staticmethod
    @tool("create_payment_tool", args_schema=PaymentSchemaIn)
    def create_payment(
        booking_id              : UUID
        , amount                : Decimal
        , payment_method        : str
        , transaction_date      : datetime
        , transaction_reference : Optional[str] = None
    ) -> Dict:
        """
        Create a new payment for a booking.
        
        Args:
            booking_id           : UUID of the booking
            amount               : Payment amount
            payment_method       : Method of payment
            transaction_date     : Date of transaction
            transaction_reference: Optional transaction reference
            
        Returns:
            Dict containing created payment information
        """
        try:
            data = {
                "booking_id"             : str(booking_id)
                , "amount"               : str(amount)
                , "payment_method"       : payment_method
                , "transaction_date"     : transaction_date.isoformat()
                , "transaction_reference": transaction_reference
            }
            
            response = APIUtils.post(
                endpoint = "/api/v1/payment"
                , data   = data
            )
            
            logger.info(
                "Payment created successfully"
                , extra = {
                    "booking_id": str(booking_id)
                    , "amount"  : str(amount)
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to create payment: {str(e)}")
            raise

    @staticmethod
    @tool("get_payment_tool")
    def get_payment(
        payment_id: UUID
    ) -> Dict:
        """
        Get payment details by ID.
        
        Args:
            payment_id: UUID of the payment
            
        Returns:
            Dict containing payment information
        """
        try:
            response = APIUtils.get(
                endpoint = f"/api/v1/payment/{payment_id}"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get payment: {str(e)}")
            raise

    @staticmethod
    @tool("get_booking_payments_tool")
    def get_booking_payments(
        booking_id   : UUID
        , skip       : int = 0
        , limit      : int = 100
    ) -> List[Dict]:
        """
        Get all payments for a booking.
        
        Args:
            booking_id : UUID of the booking
            skip       : Number of records to skip
            limit      : Maximum number of records to return
            
        Returns:
            List of payment records
        """
        try:
            params = {
                "skip"  : skip
                , "limit": limit
            }
            
            response = APIUtils.get(
                endpoint = f"/api/v1/payment/booking/{booking_id}"
                , params = params
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get booking payments: {str(e)}")
            raise

    @staticmethod
    @tool("update_payment_status_tool")
    def update_payment_status(
        payment_id   : UUID
        , status     : PaymentStatus
    ) -> Dict:
        """
        Update payment status.
        
        Args:
            payment_id : UUID of the payment
            status     : New payment status
            
        Returns:
            Dict containing updated payment information
        """
        try:
            response = APIUtils.put(
                endpoint = f"/api/v1/payment/{payment_id}/status"
                , data = {"status": status.value if hasattr(status, "value") else status}
            )
            
            logger.info(
                "Payment status updated"
                , extra = {
                    "payment_id": str(payment_id)
                    , "status"  : status
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to update payment status: {str(e)}")
            raise

    @staticmethod
    @tool("void_payment_tool")
    def void_payment(
        payment_id: UUID
    ) -> bool:
        """
        Void a payment.
        
        Args:
            payment_id: UUID of the payment to void
            
        Returns:
            Boolean indicating success
        """
        try:
            APIUtils.delete(
                endpoint = f"/api/v1/payment/{payment_id}"
            )
            
            logger.info(
                "Payment voided successfully"
                , extra = {"payment_id": str(payment_id)}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to void payment: {str(e)}")
            raise

    @staticmethod
    @tool("list_payments_tool")
    def list_payments(
        skip    : int = 0
        , limit : int = 100
    ) -> List[Dict]:
        """
        Get list of all payments.

        Args:
            skip   : Number of records to skip
            limit  : Maximum number of records to return

        Returns:
            List of payment records
        """
        try:
            params = {
                "skip"  : skip
                , "limit": limit
            }

            response = APIUtils.get(
                endpoint = "/api/v1/payment/"
                , params = params
            )

            return response

        except Exception as e:
            logger.error(f"Failed to list payments: {str(e)}")
            raise
