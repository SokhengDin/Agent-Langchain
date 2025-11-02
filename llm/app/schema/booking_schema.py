from typing import Dict, Optional
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field


class BookingSchemaIn(BaseModel):
    guest_id         : UUID = Field(
        description = "UUID of the guest making the booking"
    )
    
    hotel_id         : UUID = Field(
        description = "UUID of the hotel being booked"
    )
    
    room_id          : UUID = Field(
        description = "UUID of the room being booked"
    )
    
    check_in_date    : datetime = Field(
        description = "Check-in date and time"
    )
    
    check_out_date   : datetime = Field(
        description = "Check-out date and time"
    )
    
    num_guests       : int = Field(
        gt          = 0,
        description = "Number of guests for the booking"
    )
    
    # special_requests : Optional[str] = Field(
    #     default     = None,
    #     description = "Any special requests for the booking"
    # )
    
    # total_price      : Decimal = Field(
    #     decimal_places = 2,
    #     gt            = 0,
    #     description   = "Total price for the booking"
    # )
