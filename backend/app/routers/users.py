import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.models.user import User
from app.models.reel import Reel
from app.schemas.user import UserPublic
from app.schemas.reel import PaginatedReels
from app.services import reel_service
from fastapi import HTTPException

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/{username}", response_model=UserPublic)
async def get_profile(username: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reel_count_result = await db.execute(
        select(func.count()).where(Reel.creator_id == user.id, Reel.status == "published")
    )
    reel_count = reel_count_result.scalar() or 0

    return UserPublic(
        id=user.id,
        username=user.username,
        avatar_url=user.avatar_url,
        bio=user.bio,
        reel_count=reel_count,
        follower_count=0,   # Phase 2: follows system
        following_count=0,
    )


@router.get("/{username}/reels", response_model=PaginatedReels)
async def get_user_reels(
    username: str,
    cursor: str | None = Query(None),
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return await reel_service.list_reels(db, None, cursor, limit, cuisine=None)
