from typing import Dict, Optional
from uuid import UUID

from langchain_core.tools import tool

from app.core.utils.api_utils import APIUtils
from app.core.config import settings
from app import logger


class InvoiceTools:
    """Tools for managing invoice operations in the hotel system"""
    
    @staticmethod
    @tool("generate_invoice_tool")
    async def generate_invoice(
        booking_id      : UUID
    ) -> Dict:
        """
        Generate a PDF invoice for a booking.

        Args:
            booking_id  : UUID of the booking to generate invoice for

        Returns:
            Dict containing the invoice URL and details
        """
        try:
            booking_id_str  = str(booking_id)
            invoice_url     = f"{settings.API_BASE_URL}/api/v1/invoice/{booking_id_str}"

            logger.info(
                f"Invoice URL generated for booking: {booking_id_str}"
            )

            return {
                "invoice_url"   : invoice_url
                , "message"     : "Invoice URL generated successfully. Use this URL to download or view the PDF."
                , "booking_id"  : booking_id_str
                , "content_type": "application/pdf"
            }

        except Exception as e:
            logger.error(f"Failed to generate invoice for booking {booking_id}: {str(e)}")
            return {
                "error"         : f"Failed to generate invoice: {str(e)}"
                , "booking_id"  : str(booking_id) if booking_id else "unknown"
            }

    @staticmethod
    @tool("email_invoice_tool")
    async def email_invoice(
        booking_id    : UUID
        , email_address : Optional[str] = None
    ) -> Dict:
        """
        Send an invoice by email to the guest.
        
        Args:
            booking_id     : UUID of the booking
            email_address  : Optional email address to override the guest's email
            
        Returns:
            Dict containing the status of the email operation
        """
        try:
    
            booking_id_str  = str(booking_id)
        
            data            = {}
            if email_address is not None:
                data["email_address"] = email_address
            
    
            response = await APIUtils.post(
                endpoint = f"{settings.API_BASE_URL}/api/v1/invoice/{booking_id_str}/email"
                , data   = data
            )
            
            logger.info(
                f"Invoice emailed successfully for booking: {booking_id_str}"
            )
            
            return response or {
                "status": "success",
                "message": f"Invoice for booking {booking_id_str} has been emailed successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to email invoice for booking {booking_id}: {str(e)}")

            return {
                "error": f"Failed to email invoice: {str(e)}",
                "booking_id": str(booking_id) if booking_id else "unknown",
                "status": "failed"
            }