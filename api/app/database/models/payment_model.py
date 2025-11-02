import uuid
from decimal import Decimal
from datetime import datetime

from sqlalchemy import Column, String, Integer, ForeignKey, UUID, TIMESTAMP, func, Boolean, Text, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.enum.enum import PaymentStatus

from app.database.models.base_model import Base



class PaymentModel(Base):

   __tablename__   = "payments"

   id              : Mapped[uuid.UUID]    = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

   booking_id      : Mapped[uuid.UUID]    = mapped_column(ForeignKey("bookings.id"), nullable=False)

   amount          : Mapped[Decimal]      = mapped_column(Numeric(10,2), nullable=False)

   payment_method  : Mapped[str]          = mapped_column(String(50), nullable=False)

   transaction_date: Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), nullable=False)
   
   payment_status  : Mapped[str]          = mapped_column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)

   transaction_reference: Mapped[str]     = mapped_column(String(100), nullable=True)

   created_at      : Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
   updated_at      : Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), nullable=True)
   deleted_at      : Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), nullable=True)

   is_active       : Mapped[bool]         = mapped_column(Boolean, default=True)

   # Relationship
   booking         = relationship("BookingModel", back_populates="payments")