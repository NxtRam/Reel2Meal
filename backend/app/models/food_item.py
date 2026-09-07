import uuid
from datetime import datetime

from sqlalchemy import String, Text, Numeric, Boolean, DateTime, ForeignKey, func
from app.utils.guid_type import GUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FoodItem(Base):
    __tablename__ = "food_items"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    reel_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("reels.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_veg: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    reel: Mapped["Reel"] = relationship("Reel", back_populates="food_items")
