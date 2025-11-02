from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timezone
import secrets

from app.database.models.guest_model import GuestModel
from app.database.schemas.auth_schema import RegisterSchema, LoginSchema, TokenSchema
from app.core.security import get_password_hash, verify_password, create_access_token

from app import logger

class AuthService:

    @staticmethod
    def register(db: Session, data: RegisterSchema) -> TokenSchema:
        existing = db.query(GuestModel).filter(
            and_(
                GuestModel.email == data.email
                , GuestModel.is_active == True
            )
        ).first()

        if existing:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST
                , detail    = "Email already registered"
            )

        hashed_password = get_password_hash(data.password)

        guest = GuestModel(
            first_name      = data.first_name
            , last_name     = data.last_name
            , email         = data.email
            , phone_number  = data.phone_number
            , password      = hashed_password
        )

        db.add(guest)
        db.commit()
        db.refresh(guest)

        # Generate session token
        session_token       = secrets.token_urlsafe(32)
        guest.session_token = session_token
        guest.last_login_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(guest)

        access_token = create_access_token(data={"sub": str(guest.id), "session": session_token})

        return TokenSchema(access_token=access_token)

    @staticmethod
    def login(db: Session, data: LoginSchema) -> TokenSchema:
        guest = db.query(GuestModel).filter(
            and_(
                GuestModel.email == data.email
                , GuestModel.is_active == True
            )
        ).first()

        if not guest or not verify_password(data.password, guest.password):
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED
                , detail    = "Invalid credentials"
            )

        # Generate new session token for this login
        session_token       = secrets.token_urlsafe(32)
        guest.session_token = session_token
        guest.last_login_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(guest)

        access_token = create_access_token(data={"sub": str(guest.id), "session": session_token})

        return TokenSchema(access_token=access_token)

    @staticmethod
    def logout(db: Session, guest: GuestModel) -> None:
        """Invalidate current session by clearing session token and updating logout time"""
        guest.session_token  = None
        guest.last_logout_at = datetime.now(timezone.utc)
        db.commit()
