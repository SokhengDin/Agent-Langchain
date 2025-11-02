import uuid
from uuid import UUID
from datetime import datetime

from sqlalchemy import Column, String, Integer, ForeignKey, UUID, TIMESTAMP, func, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database.models.base_model import Base


class GuestModel(Base):

   __tablename__   = "guests"

   id              : Mapped[UUID]         = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

   first_name      : Mapped[str]          = mapped_column(String, nullable=False)
   last_name       : Mapped[str]          = mapped_column(String, nullable=False)

   email           : Mapped[str]          = mapped_column(String, nullable=False, unique=True)
   phone_number    : Mapped[str]          = mapped_column(String, nullable=False)
   password        : Mapped[str]          = mapped_column(String, nullable=False)

   address         : Mapped[str]          = mapped_column(String, nullable=True)
   nationality     : Mapped[str]          = mapped_column(String, nullable=True)

   passport_number : Mapped[str]          = mapped_column(String, nullable=True)

   created_at      : Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
   updated_at      : Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), nullable=True)
   deleted_at      : Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), nullable=True)

   # Session tracking to invalidate old tokens
   last_login_at   : Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), nullable=True)
   last_logout_at  : Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), nullable=True)
   session_token   : Mapped[str]          = mapped_column(String, nullable=True)  # Unique identifier for current session

   is_active       : Mapped[bool]         = mapped_column(Boolean, default=True)

   # Relationships
   bookings                               = relationship("BookingModel", back_populates="guest")
   reviews                                = relationship("ReviewModel", back_populates="guest")