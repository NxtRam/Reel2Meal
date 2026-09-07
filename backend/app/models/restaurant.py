import uuid
from datetime import datetime

from sqlalchemy import String, Text, Numeric, DateTime, ForeignKey, func
from app.utils.guid_type import GUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    contact: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    reel_restaurants: Mapped[list["ReelRestaurant"]] = relationship(
        "ReelRestaurant", back_populates="restaurant", cascade="all, delete-orphan"
    )


class ReelRestaurant(Base):
    __tablename__ = "reel_restaurants"

    reel_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("reels.id", ondelete="CASCADE"), primary_key=True
    )
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("restaurants.id", ondelete="CASCADE"), primary_key=True
    )

    reel: Mapped["Reel"] = relationship("Reel", back_populates="reel_restaurants")
    restaurant: Mapped["Restaurant"] = relationship("Restaurant", back_populates="reel_restaurants")
