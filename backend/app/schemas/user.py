import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field


# ── User ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserOut(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    avatar_url: str | None
    bio: str | None
    role: str = "user"
    restaurant_id: uuid.UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserPublic(BaseModel):
    id: uuid.UUID
    username: str
    avatar_url: str | None
    bio: str | None
    role: str = "user"
    restaurant_id: uuid.UUID | None = None
    reel_count: int = 0
    follower_count: int = 0
    following_count: int = 0

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    bio: str | None = None
    avatar_url: str | None = None


class RestaurantRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    restaurant_name: str = Field(..., min_length=1, max_length=255)
    restaurant_address: str | None = None
    restaurant_city: str | None = None
    restaurant_contact: str | None = None
