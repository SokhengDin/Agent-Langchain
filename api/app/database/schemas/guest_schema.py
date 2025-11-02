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
    password        : str = Field(min_length=8, max_length=100)
    
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

class GuestSchemaOut(BaseModel):
    id              : UUID
    
    first_name      : str
    last_name       : str
    
    email           : EmailStr
    phone_number    : str
    
    address         : Optional[str]
    nationality     : Optional[str]
    
    passport_number : Optional[str]
    
    created_at      : datetime
    updated_at      : Optional[datetime]
    deleted_at      : Optional[datetime]

    last_login_at   : Optional[datetime]
    last_logout_at  : Optional[datetime]

    is_active       : bool = True
    
    class Config:
        from_attributes = True
        json_encoders   = {
            datetime : lambda v: v.isoformat(),
            UUID     : lambda v: str(v)
        }


