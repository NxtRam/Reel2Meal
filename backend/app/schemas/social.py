import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginRequest(BaseModel):
    email: str
    password: str


class CommentOut(BaseModel):
    id: uuid.UUID
    reel_id: uuid.UUID
    user_id: uuid.UUID
    body: str
    created_at: datetime
    username: str = ""          # populated by comment_service
    avatar_initial: str = "?"   # first letter of username

    model_config = {"from_attributes": True}


class CommentCreate(BaseModel):
    body: str = Field(..., min_length=1, max_length=500, strip_whitespace=True)
