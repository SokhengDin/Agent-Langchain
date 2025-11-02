from uuid import UUID
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select, and_, func, update
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database.models.review_model import ReviewModel
from app.database.models.hotel_model import HotelModel
from app.database.schemas.review_schema import ReviewSchemaIn, ReviewSchemaOut
from loguru import logger


class ReviewService:
    
    @staticmethod
    def create_review(
        db              : Session
        , review_data   : ReviewSchemaIn
    ) -> ReviewSchemaOut:
        try:
            # Verify hotel exists
            hotel = db.query(HotelModel).filter(
                and_(
                    HotelModel.id == review_data.hotel_id
                    , HotelModel.is_active == True
                )
            ).first()
            
            if not hotel:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND
                    , detail    = f"Hotel with id {review_data.hotel_id} not found"
                )
            
            # Set review date if not provided
            if not review_data.review_date:
                review_data.review_date = datetime.now()
                
            db_review = ReviewModel(**review_data.model_dump())
            
            db.add(db_review)
            db.commit()
            db.refresh(db_review)
            
            # Update hotel rating
            ReviewService.update_hotel_rating(db, review_data.hotel_id)
            
            return ReviewSchemaOut.model_validate(db_review)
        
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating review: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = str(e)
            )
    
    @staticmethod
    def get_review_by_id(
        db              : Session
        , review_id     : UUID
    ) -> ReviewSchemaOut:
        try:
            stmt = select(
                ReviewModel
            ).where(
                and_(
                    ReviewModel.id == review_id
                    , ReviewModel.is_active == True
                )
            )
            
            review = db.execute(stmt).scalar_one_or_none()
            
            if not review:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND
                    , detail    = f"Review with id {review_id} not found"
                )
            
            return ReviewSchemaOut.model_validate(review)
        
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving review: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to retrieve review"
            )
    
    @staticmethod
    def get_hotel_reviews(
        db              : Session
        , hotel_id      : UUID
        , skip          : int = 0
        , limit         : int = 100
    ) -> List[ReviewSchemaOut]:
        try:
            stmt = select(
                ReviewModel
            ).where(
                and_(
                    ReviewModel.hotel_id == hotel_id
                    , ReviewModel.is_active == True
                )
            ).order_by(
                ReviewModel.review_date.desc()
            ).offset(skip).limit(limit)
            
            reviews = db.execute(stmt).scalars().all()
            
            return [ReviewSchemaOut.model_validate(review) for review in reviews]
        
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving hotel reviews: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to retrieve hotel reviews"
            )
    
    @staticmethod
    def update_review(
        db              : Session
        , review_id     : UUID
        , review_data   : ReviewSchemaIn
    ) -> ReviewSchemaOut:
        try:
            # Verify review exists
            existing_review = ReviewService.get_review_by_id(db, review_id)
            
            update_data = review_data.model_dump()
            
            stmt = update(
                ReviewModel
            ).where(
                and_(
                    ReviewModel.id == review_id
                    , ReviewModel.is_active == True
                )
            ).values(
                **update_data
                , updated_at = datetime.now()
            ).returning(ReviewModel)
            
            result = db.execute(stmt)
            db.commit()
            
            updated_review = result.scalar_one_or_none()
            
            # Update hotel rating
            ReviewService.update_hotel_rating(db, review_data.hotel_id)
            
            return ReviewSchemaOut.model_validate(updated_review)
        
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error updating review: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to update review"
            )
    
    @staticmethod
    def delete_review(
        db              : Session
        , review_id     : UUID
    ) -> bool:
        try:
            review = ReviewService.get_review_by_id(db, review_id)
            
            stmt = update(
                ReviewModel
            ).where(
                and_(
                    ReviewModel.id == review_id
                    , ReviewModel.is_active == True
                )
            ).values(
                is_active    = False
                , deleted_at = datetime.now()
            )
            
            result = db.execute(stmt)
            db.commit()
            
            if result.rowcount == 0:
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND
                    , detail    = f"Review with id {review_id} not found"
                )
            
            # Update hotel rating
            ReviewService.update_hotel_rating(db, review.hotel_id)
            
            return True
        
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error deleting review: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to delete review"
            )
            
    @staticmethod
    async def update_hotel_rating(
        db          : Session
        , hotel_id  : UUID
    ):
        try:
            # Calculate average rating
            avg_rating = db.query(
                func.avg(ReviewModel.rating)
            ).filter(
                and_(
                    ReviewModel.hotel_id == hotel_id
                    , ReviewModel.is_active == True
                    , ReviewModel.rating.isnot(None)
                )
            ).scalar()
            
            if avg_rating:
                # Update hotel rating
                stmt = update(
                    HotelModel
                ).where(
                    HotelModel.id == hotel_id
                ).values(
                    star_rating = round(Decimal(avg_rating), 2)
                    , updated_at = datetime.now()
                )
                
                db.execute(stmt)
                db.commit()
                
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error updating hotel rating: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Failed to update hotel rating"
            )