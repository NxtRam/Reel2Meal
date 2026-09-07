import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, func
from app.utils.guid_type import GUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Like(Base):
    __tablename__ = "likes"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    reel_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("reels.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="likes")
    reel: Mapped["Reel"] = relationship("Reel", back_populates="likes")


class Save(Base):
    __tablename__ = "saves"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    reel_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("reels.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="saves")
    reel: Mapped["Reel"] = relationship("Reel", back_populates="saves")


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(), primary_key=True, default=uuid.uuid4
    )
    reel_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("reels.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="comments")
    reel: Mapped["Reel"] = relationship("Reel", back_populates="comments")
