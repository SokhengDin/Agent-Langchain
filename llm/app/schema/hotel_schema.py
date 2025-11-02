from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional

from langchain_core.tools import StructuredTool

class HotelSearchInput(BaseModel):
    search_term: Optional[str] = Field(
        None, 
        description     = "Name or description keywords",
        examples        = ["luxury", "beach resort"]
    )
    city: Optional[str] = Field(
        None,
        description     = "City to search in",
        examples        = ["Paris", "New York"]
    )
    min_rating: Optional[Decimal] = Field(
        None
        , ge            = 1.0
        , le            = 5.0
        , decimal_places= 1
        , description   = "Minimum star rating (1.0-5.0)"
        , examples       = [4.0, 4.5]
    )
    skip: int = Field(
        0,
        ge                = 0
        , description     = "Number of results to skip for pagination"
    )
    limit: int = Field(
        5  
        , ge              = 1
        , le              = 20
        , description     = "Number of results to return (1-20)"
    )

    @field_validator("min_rating", mode='before')
    def validate_min_rating(cls, value):
        if value is None or value == "":
            return None
        try:
            decimal_val = Decimal(str(value))
            return round(decimal_val, 1)
        except:
            return None