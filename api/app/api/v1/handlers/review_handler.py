from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from app.services.review_service import ReviewService
from app.database.schemas.review_schema import ReviewSchemaIn, ReviewSchemaOut
from app.database import get_db
from loguru import logger

router = APIRouter()


@router.post(
    "/"
    , response_model  = ReviewSchemaOut
    , status_code    = status.HTTP_201_CREATED
)
def create_review(
    review_data  : ReviewSchemaIn
    , db         : Session = Depends(get_db)
) -> ReviewSchemaOut:
    logger.info("Creating new review")
    
    review = ReviewService.create_review(
        db            = db
        , review_data = review_data
    )
    
    logger.info(
        "Review created successfully"
        , extra = {
            "review_id" : str(review.id)
            , "hotel_id": str(review.hotel_id)
        }
    )
    
    return review


@router.get(
    "/{review_id}"
    , response_model = ReviewSchemaOut
)
def get_review(
    review_id    : UUID
    , db         : Session = Depends(get_db)
) -> ReviewSchemaOut:
    return ReviewService.get_review_by_id(
        db           = db
        , review_id  = review_id
    )


@router.get(
    "/hotel/{hotel_id}"
    , response_model = List[ReviewSchemaOut]
)
def get_hotel_reviews(
    hotel_id    : UUID
    , skip      : int = 0
    , limit     : int = 100
    , db        : Session = Depends(get_db)
) -> List[ReviewSchemaOut]:
    return ReviewService.get_hotel_reviews(
        db          = db
        , hotel_id  = hotel_id
        , skip      = skip
        , limit     = limit
    )


@router.put(
    "/{review_id}"
    , response_model = ReviewSchemaOut
)
def update_review(
    review_id    : UUID
    , review_data: ReviewSchemaIn
    , db         : Session = Depends(get_db)
) -> ReviewSchemaOut:
    logger.info(f"Updating review: {review_id}")
    
    review = ReviewService.update_review(
        db            = db
        , review_id   = review_id
        , review_data = review_data
    )
    
    logger.info(
        "Review updated successfully"
        , extra = {
            "review_id" : str(review_id)
            , "hotel_id": str(review.hotel_id)
        }
    )
    
    return review


@router.delete(
    "/{review_id}"
    , status_code = status.HTTP_204_NO_CONTENT
)
def delete_review(
    review_id    : UUID
    , db         : Session = Depends(get_db)
):
    logger.info(f"Deleting review: {review_id}")
    
    ReviewService.delete_review(
        db           = db
        , review_id  = review_id
    )
    
    logger.info(f"Review deleted: {review_id}")