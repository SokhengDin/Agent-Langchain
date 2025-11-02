from datetime import datetime
from uuid     import UUID
from pydantic import BaseModel, Field
from typing   import Optional

class ReviewSchemaIn(BaseModel):
   hotel_id        : UUID
   
   rating          : Optional[int] = Field(None, ge=1, le=5)
   
   review_text     : Optional[str]
   
   review_date     : Optional[datetime]
   
   class Config:
       from_attributes = True
       json_encoders   = {
           datetime : lambda v: v.isoformat(),
           UUID     : lambda v: str(v)
       }

class ReviewSchemaOut(BaseModel):
   id              : UUID
   
   hotel_id        : UUID
   
   rating          : Optional[int]
   
   review_text     : Optional[str]
   
   review_date     : Optional[datetime]
   
   created_at      : datetime
   updated_at      : Optional[datetime]
   deleted_at      : Optional[datetime]
   
   is_active       : bool = True
   
   class Config:
       from_attributes = True
       json_encoders   = {
           datetime : lambda v: v.isoformat(),
           UUID     : lambda v: str(v)
       }