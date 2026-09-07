import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.food_item import FoodItem
from app.models.reel import Reel
from app.schemas.food_item import MenuOut, FoodItemOut


async def get_menu_for_reel(db: AsyncSession, reel_id: uuid.UUID) -> MenuOut:
    # Verify reel exists
    reel_result = await db.execute(
        select(Reel).where(Reel.id == reel_id, Reel.status == "published")
    )
    if not reel_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reel not found")

    items_result = await db.execute(
        select(FoodItem).where(FoodItem.reel_id == reel_id).order_by(FoodItem.category, FoodItem.name)
    )
    items = items_result.scalars().all()

    # Collect distinct categories (preserving order)
    seen: set[str] = set()
    categories: list[str] = []
    for item in items:
        cat = item.category or "Other"
        if cat not in seen:
            seen.add(cat)
            categories.append(cat)

    return MenuOut(
        reel_id=reel_id,
        items=[FoodItemOut.model_validate(i) for i in items],
        categories=categories,
    )


async def get_food_item(db: AsyncSession, item_id: uuid.UUID) -> FoodItemOut:
    result = await db.execute(select(FoodItem).where(FoodItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found")
    return FoodItemOut.model_validate(item)
