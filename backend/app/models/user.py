import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, func, ForeignKey
from app.utils.guid_type import GUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    role: Mapped[str] = mapped_column(String(20), default="user", server_default="user", nullable=False)
    restaurant_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("restaurants.id", ondelete="SET NULL"), nullable=True
    )

    # relationships
    restaurant: Mapped["Restaurant | None"] = relationship("Restaurant", foreign_keys=[restaurant_id])
    reels: Mapped[list["Reel"]] = relationship("Reel", back_populates="creator", cascade="all, delete-orphan")
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    saves: Mapped[list["Save"]] = relationship("Save", back_populates="user", cascade="all, delete-orphan")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user", cascade="all, delete-orphan")
