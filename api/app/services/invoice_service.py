import qrcode
import base64

from weasyprint import HTML
from io import BytesIO
from jinja2 import Environment, FileSystemLoader
from fastapi import Depends
from sqlalchemy.orm import Session
from uuid import UUID
import os
from datetime import datetime

from app.database.models.booking_model import BookingModel
from app.database.models.guest_model import GuestModel
from app.database.models.hotel_model import HotelModel
from app.database.models.room_model import RoomModel


class InvoiceService:
    
    @staticmethod
    def generate_qr_code(payment_url: str) -> str:
        """Generate QR code for the payment URL and return base64 encoded image"""
        qr = qrcode.QRCode(
            version             = 1,
            error_correction    = qrcode.constants.ERROR_CORRECT_L,
            box_size            = 10,
            border              = 4,
        )
        qr.add_data(payment_url)
        qr.make(fit=True)
        
        img         = qr.make_image(fill_color="black", back_color="white")
        
        buffered    = BytesIO()
        img.save(buffered)
        img_str     = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    @staticmethod
    def generate_invoice_pdf(
        booking_info: dict
    ) -> bytes:
        """Generate a PDF invoice for a booking"""
    
        payment_url     = f"https://llm_agent.dev/pay/{booking_info['booking_id']}"
        
        qr_code         = InvoiceService.generate_qr_code(payment_url)
        

        template_dir    = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../templates')
        env             = Environment(loader=FileSystemLoader(template_dir))
        template        = env.get_template('invoice_template.html')
        

        invoice_date    = datetime.now().strftime("%Y-%m-%d")

        invoice_number  = f"INV-{datetime.now().strftime('%Y%m%d')}-{booking_info['booking_id'][-8:]}"

        html_content    = template.render(
            invoice_number      = invoice_number,
            invoice_date        = invoice_date,
            booking             = booking_info,
            qr_code             = qr_code,
            payment_url         = payment_url
        )
        

        pdf             = HTML(string=html_content).write_pdf()
        
        return pdf
    
    @staticmethod
    def get_invoice(
        db          : Session,
        booking_id:  UUID
    ) -> bytes:
        """Retrieve booking info and generate invoice"""
        
        booking_data = (
            db.query(
                BookingModel,
                GuestModel,
                HotelModel,
                RoomModel
            )
            .join(GuestModel, BookingModel.guest_id == GuestModel.id)
            .join(HotelModel, BookingModel.hotel_id == HotelModel.id)
            .join(RoomModel, BookingModel.room_id == RoomModel.id)
            .filter(BookingModel.id == booking_id)
            .first()
        )
        
        if not booking_data:
            raise ValueError(f"Booking with id {booking_id} not found")
        
        booking, guest, hotel, room = booking_data
        
        
        booking_info = {
            "booking_id"        : str(booking.id),
            "guest_id"          : str(guest.id),
            "guest_name"        : f"{guest.first_name} {guest.last_name}",
            "guest_email"       : guest.email,
            "hotel_name"        : hotel.name,
            "hotel_address"     : hotel.address,
            "room_number"       : room.room_number,
            "room_type"         : room.room_type.value,
            "check_in_date"     : booking.check_in_date.date().isoformat(),
            "check_out_date"    : booking.check_out_date.date().isoformat(),
            "stay_duration"     : (booking.check_out_date.date() - booking.check_in_date.date()).days,
            "price_per_night"   : float(room.price_per_night),
            "total_price"       : float(booking.total_price),
            "booking_status"    : booking.booking_status.value,
            "num_guests"        : booking.num_guests,
            "special_requests"  : booking.special_requests or "None"
        }
        
        return InvoiceService.generate_invoice_pdf(booking_info)