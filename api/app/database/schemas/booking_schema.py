from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Optional

from app.core.enum.enum import BookingStatus

class BookingSchemaIn(BaseModel):
    
    guest_id         : UUID
    hotel_id         : UUID
    room_id          : UUID
    
    check_in_date    : datetime 
    check_out_date   : datetime 
    
    num_guests       : int = Field(gt=0)
    special_requests : Optional[str] = None

   
    @field_validator('check_in_date', 'check_out_date', mode='before')
    @classmethod
    def parse_date(cls, value):
        """Convert simple date string to datetime object if needed"""
        if isinstance(value, str):
           
            if len(value) == 10 and value[4] == '-' and value[7] == '-':
                try:
                   
                    return datetime.strptime(value, "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0)
                except ValueError:
                    pass
        return value
    
    @model_validator(mode='after')
    def validate_dates(self) -> 'BookingSchemaIn':
       
        if self.check_out_date.date() <= self.check_in_date.date():
            raise ValueError('Check-out date must be after check-in date')
        return self
    
    class Config:
        from_attributes = True
        json_encoders   = {
            datetime: lambda v: v.date().isoformat(), 
            UUID    : lambda v: str(v),
            Decimal : lambda v: str(v) 
        }

class BookingSchemaOut(BaseModel):
    id               : UUID
    
    guest_id         : UUID
    hotel_id         : UUID
    room_id          : UUID
    
    check_in_date    : datetime
    check_out_date   : datetime
    
    total_price      : Decimal = Field(decimal_places=2)
    booking_status   : BookingStatus
    
    num_guests       : int
    special_requests : Optional[str] = None
    
    created_at       : datetime
    updated_at       : Optional[datetime] = None
    
    is_active        : bool = True
    
    class Config:
        from_attributes = True
        json_encoders   = {
           
            datetime : lambda v: v.date().isoformat() if v else None,
            UUID     : lambda v: str(v),
            Decimal  : lambda v: str(v)
        }