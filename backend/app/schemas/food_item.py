import uuid
from decimal import Decimal

from pydantic import BaseModel


class FoodItemOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    price: Decimal | None
    currency: str
    image_url: str | None
    category: str | None
    is_veg: bool

    model_config = {"from_attributes": True}


class MenuOut(BaseModel):
    reel_id: uuid.UUID
    items: list[FoodItemOut]
    categories: list[str]


class FoodItemCreate(BaseModel):
    name: str
    description: str | None = None
    price: Decimal | None = None
    currency: str = "INR"
    image_url: str | None = None
    category: str | None = None
    is_veg: bool = True
