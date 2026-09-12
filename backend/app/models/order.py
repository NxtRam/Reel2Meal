import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import String, Text, Numeric, DateTime, ForeignKey, func, Enum
from app.utils.guid_type import GUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class OrderStatus(str, PyEnum):
    pending = "pending"
    confirmed = "confirmed"
    delivering = "delivering"
    cancelled = "cancelled"


class PaymentStatus(str, PyEnum):
    unpaid = "unpaid"
    paid = "paid"
    failed = "failed"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reel_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("reels.id", ondelete="SET NULL"), nullable=True, index=True
    )
    food_item_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("food_items.id", ondelete="SET NULL"), nullable=True
    )
    restaurant_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("restaurants.id", ondelete="SET NULL"), nullable=True
    )
    quantity: Mapped[int] = mapped_column(default=1, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=OrderStatus.pending, nullable=False, index=True
    )
    # Payment tracking
    payment_status: Mapped[str] = mapped_column(
        String(20), default=PaymentStatus.unpaid, nullable=False, index=True
    )
    razorpay_order_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    razorpay_payment_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="orders")
    reel: Mapped["Reel"] = relationship("Reel", back_populates="orders")
