from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from app.services.guest_service import GuestService
from app.database.schemas.guest_schema import GuestSchemaIn, GuestSchemaOut
from app.database import get_db
from app import logger

router = APIRouter()


@router.post(
    ""
    , response_model  = GuestSchemaOut
    , status_code    = status.HTTP_201_CREATED
)
def create_guest(
    guest_data   : GuestSchemaIn
    , db         : Session = Depends(get_db)
) -> GuestSchemaOut:
    logger.info("Creating new guest")
    
    guest = GuestService.create_guest(
        db         = db
        , guest_data = guest_data
    )
    
    logger.info(
        "Guest created successfully"
        , extra = {"guest_id": str(guest.id)}
    )
    
    return guest

@router.get(
    "/search"
    , response_model = List[GuestSchemaOut]
)
def search_guests(
    search_term : str
    , skip      : int = 0
    , limit     : int = 100
    , db        : Session = Depends(get_db)
) -> List[GuestSchemaOut]:
    return GuestService.search_guests(
        db            = db
        , search_term = search_term
        , skip        = skip
        , limit       = limit
    )

@router.get(
    "/{guest_id}"
    , response_model = GuestSchemaOut
)
def get_guest(
    guest_id    : UUID
    , db        : Session = Depends(get_db)
) -> GuestSchemaOut:
    return GuestService.get_guest_by_id(
        db        = db
        , guest_id = guest_id
    )


@router.get(
    "/email/{email}"
    , response_model = GuestSchemaOut
)
def get_guest_by_email(
    email   : str
    , db    : Session = Depends(get_db)
) -> GuestSchemaOut:
    return GuestService.get_guest_by_email(
        db      = db
        , email = email
    )


@router.get(
    "/"
    , response_model = List[GuestSchemaOut]
)
def list_guests(
    skip     : int = 0
    , limit  : int = 100
    , db     : Session = Depends(get_db)
) -> List[GuestSchemaOut]:
    return GuestService.list_all_guests(
        db      = db
        , skip  = skip
        , limit = limit
    )


@router.put(
    "/{guest_id}"
    , response_model = GuestSchemaOut
)
def update_guest(
    guest_id     : UUID
    , guest_data : GuestSchemaIn
    , db         : Session = Depends(get_db)
) -> GuestSchemaOut:
    logger.info(f"Updating guest: {guest_id}")
    
    guest = GuestService.update_guest(
        db          = db
        , guest_id  = guest_id
        , guest_data = guest_data
    )
    
    logger.info(
        "Guest updated successfully"
        , extra = {"guest_id": str(guest_id)}
    )
    
    return guest


@router.delete(
    "/{guest_id}"
    , status_code = status.HTTP_204_NO_CONTENT
)
def delete_guest(
    guest_id    : UUID
    , db        : Session = Depends(get_db)
):
    logger.info(f"Deleting guest: {guest_id}")
    
    GuestService.delete_guest(
        db          = db
        , guest_id  = guest_id
    )
    
    logger.info(f"Guest deleted: {guest_id}")
