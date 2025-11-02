from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.database.models.guest_model import GuestModel
from app.core.security import decode_access_token

security = HTTPBearer()

def get_current_guest(
    credentials : HTTPAuthorizationCredentials = Depends(security)
    , db        : Session = Depends(get_db)
) -> GuestModel:
    token   = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED
            , detail    = "Invalid token"
        )

    guest_id = payload.get("sub")
    session_token = payload.get("session")

    if not guest_id:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED
            , detail    = "Invalid token payload"
        )

    guest = db.query(GuestModel).filter(
        GuestModel.id == UUID(guest_id)
        , GuestModel.is_active == True
    ).first()

    if not guest:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED
            , detail    = "Guest not found"
        )

    # Validate session token - reject if token doesn't match current session
    if not session_token or guest.session_token != session_token:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED
            , detail    = "Session expired or invalid. Please login again."
        )

    return guest
