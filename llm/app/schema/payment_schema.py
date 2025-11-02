from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional

from app.core.enum.enum import PaymentStatus

class PaymentSchemaIn(BaseModel):
   booking_id           : UUID
   
   amount              : Decimal = Field(decimal_places=2, gt=0)
   
   payment_method      : str = Field(max_length=50)
   
   transaction_date    : datetime
   
   transaction_reference: Optional[str] = Field(None, max_length=100)
   
   class Config:
       from_attributes = True
       json_encoders   = {
           datetime : lambda v: v.isoformat(),
           UUID     : lambda v: str(v),
           Decimal  : lambda v: str(v)
       }

class PaymentSchemaOut(BaseModel):
   id                  : UUID
   
   booking_id          : UUID
   
   amount              : Decimal
   
   payment_method      : str
   
   transaction_date    : datetime
   
   payment_status      : PaymentStatus
   
   transaction_reference: Optional[str]
   
   created_at          : datetime
   updated_at          : Optional[datetime]
   deleted_at          : Optional[datetime]
   
   is_active          : bool = True
   
   class Config:
       from_attributes = True
       json_encoders   = {
           datetime : lambda v: v.isoformat(),
           UUID     : lambda v: str(v),
           Decimal  : lambda v: str(v)
       }