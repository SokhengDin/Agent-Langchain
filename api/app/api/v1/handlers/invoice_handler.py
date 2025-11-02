from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from uuid import UUID

from app.services.invoice_service import InvoiceService
from app.database import get_db
from app import logger

router = APIRouter()

@router.get(
    "/{booking_id}"
    , response_class = Response
    , responses      = {
        200: {
            "content": {"application/pdf": {}}
        }
    }
)
def get_invoice(
    booking_id    : UUID,
    db            : Session = Depends(get_db)
):
    """
    Generate and return a PDF invoice for a booking with a QR code for payment.
    """
    logger.info(f"Generating invoice for booking: {booking_id}")
    
    try:
        pdf_content = InvoiceService.get_invoice(
            db          = db,
            booking_id  = booking_id
        )

        headers = {
            'Content-Disposition'   : f'attachment; filename="invoice_{booking_id}.pdf"',
            'Content-Type'          : 'application/pdf',
        }
        
        response        = Response(
            content     = pdf_content,
            media_type  = "application/pdf",
            headers     = headers
        )

        response.headers["Content-Disposition"] = f"inline; filename=invoice_{booking_id}.pdf"
        
        logger.info(f"Successfully generated invoice for booking: {booking_id}")
        
        return response
        
    except HTTPException as e:
        
        raise
    except Exception as e:
        logger.error(f"Unexpected error generating invoice: {str(e)}")
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail      = f"Error generating invoice"
        )