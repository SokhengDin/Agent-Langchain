from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional

class HotelSchemaIn(BaseModel):
   name            : str = Field(min_length=2, max_length=100)
   
   address         : str = Field(max_length=200)
   city            : str = Field(max_length=100)
   
   postal_code     : Optional[str] = Field(None, max_length=20)
   phone_number    : Optional[str] = Field(None, max_length=20)
   
   email           : Optional[EmailStr]
   
   total_rooms     : int = Field(gt=0)
   
   star_rating     : Optional[Decimal] = Field(None, decimal_places=2)
   
   description     : Optional[str] = None
   
   class Config:
       from_attributes = True
       json_encoders   = {
           datetime : lambda v: v.isoformat()
       }

class HotelSchemaOut(BaseModel):
   id              : UUID
   
   name            : str
   
   address         : str
   city            : str
   
   postal_code     : Optional[str]
   phone_number    : Optional[str]
   
   email           : Optional[str]
   
   total_rooms     : int
   
   star_rating     : Optional[Decimal]
   
   description     : Optional[str]
   
   created_at      : datetime
   updated_at      : Optional[datetime]
   deleted_at      : Optional[datetime]
   
   is_active       : bool = True
   
   class Config:
       from_attributes = True
       json_encoders   = {
           datetime : lambda v: v.isoformat(),
           UUID     : lambda v: str(v),
           Decimal  : lambda v: str(v)
       }