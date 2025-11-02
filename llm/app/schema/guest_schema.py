from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional

class GuestSchemaIn(BaseModel):
    first_name      : str = Field(min_length=2, max_length=50)
    last_name       : str = Field(min_length=2, max_length=50)
    
    email           : EmailStr
    phone_number    : str = Field(min_length=8, max_length=15)
    
    address         : Optional[str] = Field(None, max_length=200)
    nationality     : Optional[str] = Field(None, max_length=50)
    
    passport_number : Optional[str] = Field(None, max_length=50)
    
    @field_validator('phone_number')
    def validate_phone(cls, v):
        if not v.replace('+', '').replace('-', '').isdigit():
            raise ValueError('Phone number must contain only digits, + and -')
        return v
    
    class Config:
        from_attributes = True
        json_encoders   = {
            datetime : lambda v: v.isoformat()
        }


class GuestSearchInput(BaseModel):
    search_term    : str = Field(
        min_length          = 2
        , max_length        = 100
    )
    skip          : Optional[int] = Field(default=0)
    limit         : Optional[int] = Field(default=100)

class GuestUpdateInput(BaseModel):
    guest_id        : UUID
    first_name      : Optional[str]         = Field(default=None, min_length=2, max_length=50)
    last_name       : Optional[str]         = Field(default=None, min_length=2, max_length=50)
    email           : Optional[EmailStr]    = Field(default=None)
    phone_number    : Optional[str]         = Field(default=None, min_length=8, max_length=15)
    address         : Optional[str]         = Field(default=None, max_length=200)
    nationality     : Optional[str]         = Field(default=None, max_length=50)
    passport_number : Optional[str]         = Field(default=None, max_length=50)