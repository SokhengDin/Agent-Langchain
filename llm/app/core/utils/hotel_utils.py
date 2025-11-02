import httpx

from fastapi import HTTPException, status
from typing import Optional, Dict, Any, Union, List
from urllib.parse import urljoin

from app.core.utils.api_utils import APIUtils
from app.core.config import settings
from loguru import logger


class HotelUtils:

    
    @staticmethod
    async def get_all_hotel_name() -> List[dict]:
        try:
            response    = await APIUtils.get(
                endpoint   = '/api/v1/hotel/'
            )

            return response

        except Exception as e:
            logger.error(f"{str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = str(e)
            )