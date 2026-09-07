import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.schemas.food_item import MenuOut, FoodItemOut
from app.services import menu_service

router = APIRouter(prefix="/menu", tags=["Menu"])


@router.get("/reel/{reel_id}", response_model=MenuOut)
async def get_reel_menu(reel_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await menu_service.get_menu_for_reel(db, reel_id)


@router.get("/item/{item_id}", response_model=FoodItemOut)
async def get_food_item(item_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await menu_service.get_food_item(db, item_id)
