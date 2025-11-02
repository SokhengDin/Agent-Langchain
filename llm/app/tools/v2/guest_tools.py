from typing import Dict, List, Optional, Union, Annotated
from uuid import UUID

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app.schema.guest_schema import GuestSchemaIn, GuestSearchInput, GuestUpdateInput

from app.core.utils.api_utils_sync import APIUtils

from app import logger

class GuestTools:
    """Tools for managing guest operations in the hotel system"""

    @staticmethod
    @tool("get_guest_tool")
    async def get_guest(
        state           : Annotated[Dict, InjectedState]
    ) -> Dict:
        """
        Retrieve guest information by token

        Returns:
            Dict containing the guest information
        """
        try:
            token       = state.get("token", "")

            if not token:
                return {
                    "status": 401
                    , "message": "No authentication token provided"
                    , "data": None
                }

            response    = APIUtils.get(
                endpoint    = f"/api/v1/auth/me"
                , headers   = {
                    "Authorization": f"Bearer {token}"
                }
            )

            return response

        except Exception as e:
            logger.error(f"Error getting guest: {str(e)}")
            raise
   
    @tool("update_guest_tool", args_schema=GuestUpdateInput)
    async def update_guest(
        guest_id          : UUID
        , first_name        : Optional[str] = None
        , last_name         : Optional[str] = None
        , email             : Optional[str] = None
        , phone_number      : Optional[str] = None
        , address           : Optional[str] = None
        , nationality       : Optional[str] = None
        , passport_number   : Optional[str] = None
    ) -> Dict:
        """
        Update guest information.
        
        Args:
            guest_id        : The UUID of the guest to update
            first_name      : Optional new first name
            last_name       : Optional new last name
            email           : Optional new email
            phone_number    : Optional new phone number
            address         : Optional new address
            nationality     : Optional new nationality
            passport_number: Optional new passport number
            
        Returns:
            Dict containing the updated guest information
        """
        try:

            update_data = {}
            if first_name is not None:
                update_data["first_name"]   = first_name
            if last_name is not None:
                update_data["last_name"]    = last_name
            if email is not None:
                update_data["email"]        = email
            if phone_number is not None:
                update_data["phone_number"] = phone_number
            if address is not None:
                update_data["address"]      = address
            if nationality is not None:
                update_data["nationality"]  = nationality
            if passport_number is not None:
                update_data["passport_number"] = passport_number
                
            response = APIUtils.put(
                endpoint = f"/api/v1/guest/{guest_id}"
                , data   = update_data
            )
            
            logger.info(
                "Guest updated successfully"
                , extra = {"guest_id": str(guest_id)}
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to update guest {guest_id}: {str(e)}")
            raise
