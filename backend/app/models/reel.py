import uuid
from datetime import datetime

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, func
from app.utils.guid_type import GUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Reel(Base):
    __tablename__ = "reels"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    creator_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    video_url: Mapped[str] = mapped_column(Text, nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cuisine_tag: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="published", nullable=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    like_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # Denormalized counters kept in-sync by the service layer for fast feed scoring
    save_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    watch_time_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    audio_url: Mapped[str | None] = mapped_column(Text, nullable=True)  # background music track
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # relationships
    creator: Mapped["User"] = relationship("User", back_populates="reels")
    food_items: Mapped[list["FoodItem"]] = relationship("FoodItem", back_populates="reel", cascade="all, delete-orphan")
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="reel", cascade="all, delete-orphan")
    saves: Mapped[list["Save"]] = relationship("Save", back_populates="reel", cascade="all, delete-orphan")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="reel", cascade="all, delete-orphan")
    reel_restaurants: Mapped[list["ReelRestaurant"]] = relationship("ReelRestaurant", back_populates="reel", cascade="all, delete-orphan")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="reel")
