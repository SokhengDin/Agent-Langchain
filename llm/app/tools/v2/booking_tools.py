from typing import Dict, List, Optional
from uuid import UUID
from decimal import Decimal

from langchain_core.tools import tool

from app.schema.booking_schema import BookingSchemaIn
from app.core.utils.api_utils_sync import APIUtils
from app.core.enum.enum import BookingStatus
from app import logger


class BookingTools:
    """Tools for managing booking operations in the hotel system (synchronous version)"""
    
    @staticmethod
    @tool("create_booking_tool", args_schema=BookingSchemaIn)
    def create_booking(
        guest_id         : UUID,
        hotel_id         : UUID,
        room_id          : UUID,
        check_in_date    : str,
        check_out_date   : str,
        num_guests       : int,
        total_price      : Optional[Decimal] = None,
        special_requests : Optional[str] = None
    ) -> Dict:
        """
        Create a new booking for a guest.

        Args:
            guest_id         : UUID of the guest
            hotel_id         : UUID of the hotel
            room_id          : UUID of the room
            check_in_date    : Check-in date in ISO format
            check_out_date   : Check-out date in ISO format
            num_guests       : Number of guests
            total_price      : Total price for the booking (optional)
            special_requests : Optional special requests

        Returns:
            Dict containing the created booking information
        """
        try:
            if hasattr(check_in_date, 'isoformat'):
                check_in_date = check_in_date.isoformat()
            if hasattr(check_out_date, 'isoformat'):
                check_out_date = check_out_date.isoformat()

            data = {
                "guest_id"         : str(guest_id),
                "hotel_id"         : str(hotel_id),
                "room_id"          : str(room_id),
                "check_in_date"    : check_in_date,
                "check_out_date"   : check_out_date,
                "num_guests"       : num_guests
            }

            if total_price is not None:
                data["total_price"] = str(total_price)

            if special_requests is not None:
                data["special_requests"] = special_requests

            logger.info(f"Creating booking with data: {data}")

            response = APIUtils.post(
                endpoint = "/api/v1/booking",
                data     = data
            )

            logger.info("Booking created successfully")

            return response

        except Exception as e:
            logger.error(f"Failed to create booking: {str(e)}")
            raise


    @staticmethod
    @tool("check_booking_status_tool")
    def check_booking_status(
        booking_id: UUID
    ) -> Dict:
        """
        Retrieve booking information by its ID.

        Args:
            booking_id: The UUID of the booking

        Returns:
            Dict containing the booking information
        """
        try:
            response = APIUtils.get(
                endpoint = f"/api/v1/booking/{booking_id}"
            )

            return response

        except Exception as e:
            logger.error(f"Failed to retrieve booking {booking_id}: {str(e)}")
            raise


    @staticmethod
    @tool("update_booking_status_tool")
    def update_booking_status(
        booking_id      : UUID,
        booking_status  : BookingStatus
    ) -> Dict:
        """
        Update the status of a booking.

        Args:
            booking_id     : UUID of the booking
            booking_status : New booking status

        Returns:
            Dict containing the updated booking information
        """
        try:
            data = {
                "booking_status": booking_status.value if hasattr(booking_status, "value") else booking_status
            }

            response = APIUtils.put(
                endpoint = f"/api/v1/booking/{booking_id}/status",
                data     = data
            )

            logger.info("Booking status updated successfully")

            return response

        except Exception as e:
            logger.error(f"Failed to update booking status {booking_id}: {str(e)}")
            raise


    @staticmethod
    @tool("cancel_booking_tool")
    def cancel_booking(
        booking_id: UUID
    ) -> bool:
        """
        Cancel a booking in the system.

        Args:
            booking_id  : The UUID of the booking to cancel

        Returns:
            Boolean indicating success
        """
        try:
            response = APIUtils.put(
                endpoint = f"/api/v1/booking/{booking_id}/cancel"
                , data   = {}
            )

            logger.info(f"Booking {booking_id} cancelled successfully")

            if response:
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to cancel booking {booking_id}: {str(e)}")
            raise


    @staticmethod
    @tool("cancel_guest_booking_tool")
    def cancel_guest_booking(
        guest_id: UUID
    ) -> bool:
        """
        Cancel all bookings for a specific guest.

        Args:
            guest_id : The UUID of the guest whose bookings to cancel

        Returns:
            Boolean indicating success
        """
        try:
            response = APIUtils.post(
                endpoint = f"/api/v1/booking/guest/{guest_id}/cancel"
            )

            logger.info(f"Guest {guest_id} bookings cancelled successfully")

            return response if isinstance(response, bool) else True

        except Exception as e:
            logger.error(f"Failed to cancel guest bookings {guest_id}: {str(e)}")
            raise


    @staticmethod
    @tool("get_guest_bookings_tool")
    def get_guest_bookings(
        guest_id: UUID,
        skip    : int = 0,
        limit   : int = 100
    ) -> List[Dict]:
        """
        Get all bookings for a specific guest.

        Args:
            guest_id : UUID of the guest
            skip     : Number of records to skip
            limit    : Maximum number of records to return

        Returns:
            List of booking records for the guest
        """
        try:
            params = {
                "skip"  : skip,
                "limit" : limit
            }

            response = APIUtils.get(
                endpoint = f"/api/v1/booking/guest/{guest_id}/bookings",
                params   = params
            )

            return response

        except Exception as e:
            logger.error(f"Failed to get bookings for guest {guest_id}: {str(e)}")
            raise


    @staticmethod
    @tool("list_bookings_tool")
    def list_bookings(
        status     : Optional[BookingStatus] = None,
        from_date  : Optional[str] = None,
        to_date    : Optional[str] = None,
        skip       : int = 0,
        limit      : int = 100
    ) -> List[Dict]:
        """
        Get a filtered list of all bookings.

        Args:
            status    : Optional filter by booking status
            from_date : Optional filter by start date (ISO format)
            to_date   : Optional filter by end date (ISO format)
            skip      : Number of records to skip
            limit     : Maximum number of records to return

        Returns:
            List of booking records
        """
        try:
            params = {
                "status"    : status.value if hasattr(status, "value") else status,
                "from_date" : from_date,
                "to_date"   : to_date,
                "skip"      : skip,
                "limit"     : limit
            }

            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}

            response = APIUtils.get(
                endpoint = "/api/v1/booking/",
                params   = params
            )

            return response

        except Exception as e:
            logger.error(f"Failed to list bookings: {str(e)}")
            raise
