from typing import Dict, List, Optional, Union
from uuid import UUID

from langchain_core.tools import tool

from app.schema.guest_schema import GuestSchemaIn, GuestSearchInput, GuestUpdateInput

from app.core.utils.api_utils import APIUtils

from app import logger

class GuestTools:
    """Tools for managing guest operations in the hotel system"""
     
    @tool("creating_new_guest_tool", args_schema=GuestSchemaIn)
    async def create_guest(
        first_name        : str
        , last_name         : str
        , email             : str
        , phone_number      : str
        , address           : Optional[str] = None
        , nationality       : Optional[str] = None
        , passport_number   : Optional[str] = None
    ) -> Dict:
        """
        Create a new guest with the provided information.
        
        Args:
            first_name      : Guest's first name
            last_name       : Guest's last name
            email          : Guest's email address
            phone_number   : Guest's phone number
            address        : Optional guest's address
            nationality    : Optional guest's nationality
            passport_number: Optional guest's passport number
            
        Returns:
            Dict containing the created guest information
        """
        try:
            data = {
                "first_name"      : first_name
                , "last_name"     : last_name
                , "email"         : email
                , "phone_number"  : phone_number
                , "address"       : address
                , "nationality"   : nationality
                , "passport_number": passport_number
            }
            
            response = await APIUtils.post(
                endpoint = "/api/v1/guest"
                , data   = data
            )
            
            logger.info(
                "Guest created successfully"
                , extra = {"guest_id": response.get("id")}
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to create guest: {str(e)}")
            raise

    @staticmethod
    @tool("get_guest_tool")
    async def get_guest(
        guest_id        : UUID
    ) -> Dict:
        """
        Retrieve guest information by their ID.

        Args:
            guest_id    : The UUID of the guest

        Returns:
            Dict containing the guest information
        """
        try:
            response = await APIUtils.get(
                endpoint    = f"/api/v1/guest/{guest_id}"
            )

            return response

        except Exception as e:
            logger.error(f"Failed to retrieve guest {guest_id}: {str(e)}")
            raise

    @staticmethod
    @tool("get_guest_by_email_tool")
    async def get_guest_by_email(
        email           : str
    ) -> Dict:
        """
        Retrieve guest information by their email address.

        Args:
            email       : The email address of the guest

        Returns:
            Dict containing the guest information
        """
        try:
            response = await APIUtils.get(
                endpoint    = f"/api/v1/guest/email/{email}"
            )

            return response

        except Exception as e:
            logger.error(f"Failed to retrieve guest by email {email}: {str(e)}")
            raise

    @staticmethod
    @tool("list_all_guests_tool")
    async def list_guests(
        skip            : int = 0
        , limit         : int = 100
    ) -> List[Dict]:
        """
        Get list of all guests with pagination.

        Args:
            skip        : Number of records to skip
            limit       : Maximum number of records to return

        Returns:
            List of guest records
        """
        try:
            params = {
                "skip"      : skip
                , "limit"   : limit
            }

            response = await APIUtils.get(
                endpoint    = "/api/v1/guest/"
                , params    = params
            )

            return response

        except Exception as e:
            logger.error(f"Failed to list guests: {str(e)}")
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
                
            response = await APIUtils.put(
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

    @tool
    async def delete_guest(
        guest_id: UUID
    ) -> bool:
        """
        Delete a guest from the system (soft delete).
        
        Args:
            guest_id: The UUID of the guest to delete
            
        Returns:
            Boolean indicating success
        """
        try:
            await APIUtils.delete(
                endpoint = f"/guests/{guest_id}"
            )
            
            logger.info(
                "Guest deleted successfully"
                , extra = {"guest_id": str(guest_id)}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete guest {guest_id}: {str(e)}")
            raise
            
    @staticmethod
    @tool("search_guest_tool", args_schema=GuestSearchInput)
    async def search_guest(
        search_term : str
        , skip        : int = 0
        , limit       : int = 100
    ) -> List[Dict]:
        """
        Search for guests using a search term.
        
        Args:
            search_term: Term to search (name, email, phone)
            skip      : Number of records to skip
            limit     : Maximum number of records to return
            
        Returns:
            List of matching guest records
        """
        try:
            params = {
                "search_term" : search_term
                , "skip"     : skip
                , "limit"    : limit
            }

            params      = {k: v for k, v in params.items() if v is not None}
            
            response    = await APIUtils.get(
                endpoint = "/api/v1/guest/search"
                , params = params
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to search guests: {str(e)}")
            raise
