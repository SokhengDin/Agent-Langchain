from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class ReviewSchemaIn(BaseModel):
    """Schema for creating a new review"""
    hotel_id        : UUID              = Field(..., description="UUID of the hotel")
    rating          : Optional[int]     = Field(None, ge=1, le=5, description="Rating from 1 to 5")
    review_text     : Optional[str]     = Field(None, description="Review text content")
    review_date     : Optional[datetime]= Field(None, description="Date of the review")


class ReviewSchemaOut(BaseModel):
    """Schema for review output"""
    id              : UUID
    hotel_id        : UUID
    rating          : Optional[int]     = None
    review_text     : Optional[str]     = None
    review_date     : Optional[datetime]= None
    created_at      : datetime
    updated_at      : Optional[datetime]= None
    deleted_at      : Optional[datetime]= None
    is_active       : bool


class ReviewUpdateInput(BaseModel):
    """Schema for updating a review"""
    review_id       : UUID              = Field(..., description="UUID of the review to update")
    rating          : Optional[int]     = Field(None, ge=1, le=5, description="Rating from 1 to 5")
    review_text     : Optional[str]     = Field(None, description="Review text content")
    review_date     : Optional[datetime]= Field(None, description="Date of the review")
