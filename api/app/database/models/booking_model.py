import uuid
from uuid import UUID
from decimal import Decimal
from datetime import datetime

from sqlalchemy import Column, String, Integer, ForeignKey, UUID, TIMESTAMP, func, Boolean, Text, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.enum.enum import BookingStatus

from app.database.models.base_model import Base


class BookingModel(Base):

   __tablename__   = "bookings"

   id                : Mapped[UUID]          = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

   guest_id          : Mapped[UUID]          = mapped_column(ForeignKey("guests.id"), nullable=False)
   hotel_id          : Mapped[UUID]          = mapped_column(ForeignKey("hotels.id"), nullable=False)
   room_id           : Mapped[UUID]          = mapped_column(ForeignKey("rooms.id") , nullable=False)

   check_in_date     : Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), nullable=False)
   check_out_date    : Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), nullable=False)

   total_price       : Mapped[Decimal]      = mapped_column(Numeric(10,2), nullable=False)

   booking_status    : Mapped[str]          = mapped_column(SQLEnum(BookingStatus), default=BookingStatus.PENDING)

   num_guests        : Mapped[int]          = mapped_column(Integer, nullable=False)

   special_requests  : Mapped[str]          = mapped_column(String(20), nullable=True)

   created_at        : Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
   updated_at        : Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), nullable=True)
   deleted_at        : Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), nullable=True)

   is_active         : Mapped[bool]         = mapped_column(Boolean, default=True)

   # Relationships
   guest             = relationship("GuestModel", back_populates="bookings")
   hotel             = relationship("HotelModel" , back_populates="bookings")
   room              = relationship("RoomModel"   , back_populates="bookings")
   payments          = relationship("PaymentModel", back_populates="booking")