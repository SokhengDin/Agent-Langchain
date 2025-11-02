from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional

from app.core.enum.enum import RoomType

class RoomSchemaIn(BaseModel):
   hotel_id         : UUID

   room_number      : str = Field(max_length=20)

   room_type        : RoomType = Field(default=RoomType.SINGLE_ROOM)

   floor            : Optional[int]
   status           : str = Field(max_length=20)

   price_per_night  : float

   additional_notes : Optional[str]

   class Config:
       from_attributes = True
       json_encoders   = {
           datetime : lambda v: v.isoformat(),
           UUID     : lambda v: str(v)
       }

class RoomSchemaOut(BaseModel):
   id               : UUID

   hotel_id         : UUID

   room_number      : str

   room_type        : RoomType

   floor            : Optional[int]
   status           : str

   price_per_night  : float

   additional_notes : Optional[str]

   created_at       : datetime
   updated_at       : Optional[datetime]
   deleted_at       : Optional[datetime]

   is_active        : bool = True

   class Config:
       from_attributes = True
       json_encoders   = {
           datetime : lambda v: v.isoformat(),
           UUID     : lambda v: str(v)
       }