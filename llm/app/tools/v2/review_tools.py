from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime

from langchain_core.tools import tool

from app.schema.review_schema import ReviewSchemaIn, ReviewUpdateInput
from app.core.utils.api_utils_sync import APIUtils

from app import logger


class ReviewTools:
    """Tools for managing review operations in the hotel system"""

    @staticmethod
    @tool("create_review_tool", args_schema=ReviewSchemaIn)
    def create_review(
        hotel_id        : UUID
        , rating        : Optional[int]      = None
        , review_text   : Optional[str]      = None
        , review_date   : Optional[datetime] = None
    ) -> Dict:
        """
        Create a new review for a hotel.

        Args:
            hotel_id     : UUID of the hotel
            rating       : Optional rating from 1 to 5
            review_text  : Optional review text content
            review_date  : Optional date of the review

        Returns:
            Dict containing created review information
        """
        try:
            data = {
                "hotel_id" : str(hotel_id)
            }

            if rating is not None:
                data["rating"] = rating
            if review_text is not None:
                data["review_text"] = review_text
            if review_date is not None:
                data["review_date"] = review_date.isoformat() if hasattr(review_date, 'isoformat') else review_date

            response = APIUtils.post(
                endpoint = "/api/v1/review/"
                , data   = data
            )

            logger.info(
                "Review created successfully"
                , extra = {
                    "hotel_id": str(hotel_id)
                    , "rating": rating
                }
            )

            return response

        except Exception as e:
            logger.error(f"Failed to create review: {str(e)}")
            raise

    @staticmethod
    @tool("get_review_tool")
    def get_review(
        review_id   : UUID
    ) -> Dict:
        """
        Get review details by ID.

        Args:
            review_id   : UUID of the review

        Returns:
            Dict containing review information
        """
        try:
            response = APIUtils.get(
                endpoint = f"/api/v1/review/{review_id}"
            )

            return response

        except Exception as e:
            logger.error(f"Failed to get review: {str(e)}")
            raise

    @staticmethod
    @tool("get_hotel_reviews_tool")
    def get_hotel_reviews(
        hotel_id    : UUID
        , skip      : int = 0
        , limit     : int = 100
    ) -> List[Dict]:
        """
        Get all reviews for a specific hotel.

        Args:
            hotel_id    : UUID of the hotel
            skip        : Number of records to skip
            limit       : Maximum number of records to return

        Returns:
            List of review records
        """
        try:
            params = {
                "skip"  : skip
                , "limit": limit
            }

            response = APIUtils.get(
                endpoint = f"/api/v1/review/hotel/{hotel_id}"
                , params = params
            )

            return response

        except Exception as e:
            logger.error(f"Failed to get hotel reviews: {str(e)}")
            raise

    @staticmethod
    @tool("update_review_tool", args_schema=ReviewUpdateInput)
    def update_review(
        review_id     : UUID
        , rating      : Optional[int]      = None
        , review_text : Optional[str]      = None
        , review_date : Optional[datetime] = None
    ) -> Dict:
        """
        Update an existing review.

        Args:
            review_id   : UUID of the review to update
            rating      : Optional new rating from 1 to 5
            review_text : Optional new review text
            review_date : Optional new review date

        Returns:
            Dict containing updated review information
        """
        try:
            data = {}

            if rating is not None:
                data["rating"] = rating
            if review_text is not None:
                data["review_text"] = review_text
            if review_date is not None:
                data["review_date"] = review_date.isoformat() if hasattr(review_date, 'isoformat') else review_date

            response = APIUtils.put(
                endpoint = f"/api/v1/review/{review_id}"
                , data   = data
            )

            logger.info(
                "Review updated successfully"
                , extra = {"review_id": str(review_id)}
            )

            return response

        except Exception as e:
            logger.error(f"Failed to update review: {str(e)}")
            raise

    @staticmethod
    @tool("delete_review_tool")
    def delete_review(
        review_id   : UUID
    ) -> bool:
        """
        Delete a review from the system.

        Args:
            review_id   : UUID of the review to delete

        Returns:
            Boolean indicating success
        """
        try:
            APIUtils.delete(
                endpoint = f"/api/v1/review/{review_id}"
            )

            logger.info(
                "Review deleted successfully"
                , extra = {"review_id": str(review_id)}
            )

            return True

        except Exception as e:
            logger.error(f"Failed to delete review: {str(e)}")
            raise
