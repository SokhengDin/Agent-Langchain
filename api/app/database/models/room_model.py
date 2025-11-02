import uuid
from uuid import UUID
from decimal import Decimal
from typing import List
from datetime import datetime

from sqlalchemy import Float, String, Integer, ForeignKey, UUID, TIMESTAMP, func, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.enum.enum import RoomType

from app.database.models.base_model import Base


class RoomModel(Base):

   __tablename__   = "rooms"

   id              : Mapped[UUID]         = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
   
   hotel_id        : Mapped[UUID]         = mapped_column(ForeignKey("hotels.id")      , nullable=False)
   
   room_number     : Mapped[str]          = mapped_column(String(20), nullable=False)

   room_type       : Mapped[str]          = mapped_column(SQLEnum(RoomType), default=RoomType.SINGLE_ROOM)

   price_per_night : Mapped[float]        = mapped_column(Float)
   max_occupancy   : Mapped[int]          = mapped_column(Integer, default=1, nullable=False)

   floor           : Mapped[int]          = mapped_column(Integer, nullable=True)
   status          : Mapped[str]          = mapped_column(String(20), nullable=False)
   
   additional_notes: Mapped[str]          = mapped_column(Text, nullable=True)

   created_at      : Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
   updated_at      : Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), nullable=True)
   deleted_at      : Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), nullable=True)

   is_active       : Mapped[bool]         = mapped_column(Boolean, default=True)

   # Relationships
   hotel           = relationship("HotelModel", back_populates="rooms")
   bookings        = relationship("BookingModel", back_populates="room")