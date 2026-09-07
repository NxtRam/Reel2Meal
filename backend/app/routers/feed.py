from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.reel import PaginatedReels
from app.services import feed_service

router = APIRouter(prefix="/feed", tags=["Feed"])


@router.get("/", response_model=PaginatedReels)
async def get_feed(
    cursor: str | None = Query(None),
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await feed_service.get_feed(db, current_user, cursor, limit)
