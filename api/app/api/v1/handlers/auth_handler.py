from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.database.schemas.auth_schema import RegisterSchema, LoginSchema, TokenSchema
from app.database.schemas.guest_schema import GuestSchemaOut
from app.services.auth_service import AuthService
from app.api.v1.deps.auth import get_current_guest
from app.database.models.guest_model import GuestModel
from app import logger

router = APIRouter()

@router.post("/register", response_model=TokenSchema, status_code=status.HTTP_201_CREATED)
def register(data: RegisterSchema, db: Session = Depends(get_db)) -> TokenSchema:
    logger.info(f"Registering user: {data.email}")
    return AuthService.register(db, data)

@router.post("/login", response_model=TokenSchema)
def login(data: LoginSchema, db: Session = Depends(get_db)) -> TokenSchema:
    logger.info(f"Login attempt: {data.email}")
    return AuthService.login(db, data)

@router.get("/me", response_model=GuestSchemaOut)
def get_me(guest: GuestModel = Depends(get_current_guest)) -> GuestSchemaOut:
    return GuestSchemaOut.model_validate(guest)

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(guest: GuestModel = Depends(get_current_guest), db: Session = Depends(get_db)) -> dict:
    logger.info(f"Logout: {guest.email}")
    AuthService.logout(db, guest)
    return {"message": "Logged out successfully"}
