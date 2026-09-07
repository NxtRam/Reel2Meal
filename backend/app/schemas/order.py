import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    reel_id: uuid.UUID
    food_item_id: uuid.UUID | None = None
    restaurant_id: uuid.UUID | None = None
    quantity: int = Field(default=1, ge=1, le=99)
    note: str | None = None


class OrderOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    reel_id: uuid.UUID | None
    food_item_id: uuid.UUID | None
    restaurant_id: uuid.UUID | None
    quantity: int
    note: str | None
    total_price: Decimal | None
    currency: str
    status: str
    payment_status: str
    razorpay_order_id: str | None
    razorpay_payment_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(pending|confirmed|cancelled)$")
