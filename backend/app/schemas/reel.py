import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, computed_field
from app.schemas.food_item import FoodItemCreate


# ---------------------------------------------------------------------------
# Nested output shapes
# ---------------------------------------------------------------------------

class RestaurantOut(BaseModel):
    id: uuid.UUID
    name: str
    city: str | None
    address: str | None
    latitude: float | None
    longitude: float | None
    contact: str | None

    model_config = {"from_attributes": True}


class CreatorOut(BaseModel):
    id: uuid.UUID
    username: str
    avatar_url: str | None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Phase 2 scoring constants — keep in sync with feed_service.py
# ---------------------------------------------------------------------------
SCORE_WEIGHT_LIKES       = 3
SCORE_WEIGHT_SAVES       = 5
SCORE_WEIGHT_WATCH_TIME  = 1   # 1 point per second


class ReelOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    video_url: str
    thumbnail_url: str | None
    audio_url: str | None = None       # background music track for this reel
    duration_sec: int | None
    cuisine_tag: str | None
    view_count: int
    like_count: int
    save_count: int = 0
    watch_time_seconds: int = 0
    is_liked: bool = False
    is_saved: bool = False
    creator: CreatorOut
    created_at: datetime

    @computed_field  # type: ignore[misc]
    @property
    def feed_score(self) -> int:
        """
        Phase 2 feed ranking score (read-only, derived).
        score = likes * 3 + saves * 5 + watch_time_seconds * 1
        """
        return (
            self.like_count * SCORE_WEIGHT_LIKES
            + self.save_count * SCORE_WEIGHT_SAVES
            + self.watch_time_seconds * SCORE_WEIGHT_WATCH_TIME
        )

    model_config = {"from_attributes": True}


class ReelDetailOut(ReelOut):
    comment_count: int = 0
    restaurants: list[RestaurantOut] = []


class ReelCreate(BaseModel):
    title: str
    description: str | None = None
    video_url: str
    thumbnail_url: str | None = None
    audio_url: str | None = None
    duration_sec: int | None = None
    cuisine_tag: str | None = None
    food_items: list[FoodItemCreate] = []


class PaginatedReels(BaseModel):
    data: list[ReelOut]
    next_cursor: str | None
    has_more: bool


class LikeResponse(BaseModel):
    liked: bool
    like_count: int


class SaveResponse(BaseModel):
    saved: bool
    save_count: int


class WatchTimeRequest(BaseModel):
    """Body for POST /reels/{id}/watch — records how many seconds the user watched."""
    seconds: int = Field(..., ge=1, le=3600, description="Seconds watched (1–3600)")


class WatchTimeResponse(BaseModel):
    reel_id: uuid.UUID
    seconds_added: int
    watch_time_seconds: int  # new total

