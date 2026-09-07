import uuid

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_current_user, get_optional_user
from app.models.user import User
from app.schemas.reel import (
    PaginatedReels, ReelDetailOut, LikeResponse, SaveResponse,
    WatchTimeRequest, WatchTimeResponse, ReelCreate,
)
from app.services import reel_service

router = APIRouter(prefix="/reels", tags=["Reels"])


@router.get("/", response_model=PaginatedReels)
async def list_reels(
    cursor: str | None = Query(None),
    limit: int = Query(10, ge=1, le=20),
    cuisine: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    return await reel_service.list_reels(db, current_user, cursor, limit, cuisine)


@router.post("/", response_model=ReelDetailOut, status_code=201)
async def create_reel(
    data: ReelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "restaurant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only restaurants can post reels",
        )
    return await reel_service.create_reel(db, current_user, data)


@router.get("/{reel_id}", response_model=ReelDetailOut)
async def get_reel(
    reel_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    return await reel_service.get_reel_detail(db, reel_id, current_user)


@router.post("/{reel_id}/like", response_model=LikeResponse)
async def like_reel(
    reel_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await reel_service.toggle_like(db, reel_id, current_user)


@router.post("/{reel_id}/save", response_model=SaveResponse)
async def save_reel(
    reel_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await reel_service.toggle_save(db, reel_id, current_user)


@router.post(
    "/{reel_id}/watch",
    response_model=WatchTimeResponse,
    summary="Record watch time",
    description=(
        "Report how many seconds the current viewer watched this reel. "
        "Called by the frontend player on pause/exit. "
        "Increments `watch_time_seconds` and `view_count` on the reel. "
        "No authentication required."
    ),
)
async def record_watch(
    reel_id: uuid.UUID,
    body: WatchTimeRequest,
    db: AsyncSession = Depends(get_db),
):
    return await reel_service.record_watch_time(db, reel_id, body.seconds)
