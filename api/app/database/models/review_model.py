import uuid
from uuid import UUID
from datetime import datetime

from sqlalchemy import Column, String, Integer, ForeignKey, UUID, TIMESTAMP, func, Boolean, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database.models.base_model import Base


class ReviewModel(Base):

   __tablename__   = "reviews"

   id              : Mapped[UUID]         = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

   hotel_id        : Mapped[UUID]         = mapped_column(UUID(as_uuid=True), ForeignKey('hotels.id'), nullable=False)
   guest_id        : Mapped[UUID]         = mapped_column(UUID(as_uuid=True), ForeignKey('guests.id'), nullable=False)

   rating          : Mapped[int]          = mapped_column(Integer, nullable=True)

   review_text     : Mapped[str]          = mapped_column(Text, nullable=True)

   review_date     : Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), nullable=True)

   created_at      : Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
   updated_at      : Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), nullable=True)
   deleted_at      : Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), nullable=True)

   is_active       : Mapped[bool]         = mapped_column(Boolean, default=True)

   # Relationship
   hotel             = relationship("HotelModel", back_populates="reviews")
   guest             = relationship("GuestModel", back_populates="reviews")