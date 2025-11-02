import uuid
from decimal import Decimal
from datetime import datetime

from sqlalchemy import Column, String, Integer, ForeignKey, UUID, TIMESTAMP, func, Boolean, Text, Numeric
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database.models.base_model import Base


class HotelModel(Base):

    __tablename__   = "hotels"

    id              : Mapped[uuid.UUID]     = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name            : Mapped[str]          = mapped_column(String(100), nullable=False)
    
    address         : Mapped[str]          = mapped_column(String(200), nullable=False)
    city            : Mapped[str]          = mapped_column(String(100), nullable=False)
    
    postal_code     : Mapped[str]          = mapped_column(String(20), nullable=True)
    phone_number    : Mapped[str]          = mapped_column(String(20), nullable=True)
    
    email           : Mapped[str]          = mapped_column(String(100), nullable=True)
    
    total_rooms     : Mapped[int]          = mapped_column(Integer, nullable=False)
    
    star_rating     : Mapped[Decimal]      = mapped_column(Numeric(10,2), nullable=True)
    
    description     : Mapped[str]          = mapped_column(Text, nullable=True)

    created_at      : Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at      : Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    deleted_at      : Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    is_active       : Mapped[bool]         = mapped_column(Boolean, default=True)

    rooms                                  = relationship("RoomModel", back_populates="hotel")
    bookings                               = relationship("BookingModel", back_populates="hotel")
    reviews                                = relationship("ReviewModel", back_populates="hotel")