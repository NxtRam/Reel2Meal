import uuid

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.reel import Reel
from app.models.social import Like, Save, Comment
from app.models.restaurant import ReelRestaurant, Restaurant
from app.models.user import User
from app.models.food_item import FoodItem
from app.schemas.reel import (
    PaginatedReels, ReelOut, ReelDetailOut, CreatorOut,
    LikeResponse, SaveResponse, RestaurantOut,
    WatchTimeRequest, WatchTimeResponse, ReelCreate,
)
from app.utils.pagination import encode_cursor, decode_cursor


MAX_LIMIT = 20


def _build_reel_out(reel: Reel, liked_ids: set, saved_ids: set) -> ReelOut:
    return ReelOut(
        id=reel.id,
        title=reel.title,
        description=reel.description,
        video_url=reel.video_url,
        thumbnail_url=reel.thumbnail_url,
        duration_sec=reel.duration_sec,
        cuisine_tag=reel.cuisine_tag,
        view_count=reel.view_count,
        like_count=reel.like_count,
        save_count=reel.save_count,
        watch_time_seconds=reel.watch_time_seconds,
        is_liked=reel.id in liked_ids,
        is_saved=reel.id in saved_ids,
        creator=CreatorOut.model_validate(reel.creator),
        created_at=reel.created_at,
    )


async def list_reels(
    db: AsyncSession,
    current_user: User | None,
    cursor: str | None,
    limit: int,
    cuisine: str | None,
) -> PaginatedReels:
    limit = min(limit, MAX_LIMIT)
    q = (
        select(Reel)
        .where(Reel.status == "published")
        .options(selectinload(Reel.creator))
        .order_by(Reel.created_at.desc(), Reel.id.desc())
    )
    if cuisine:
        q = q.where(Reel.cuisine_tag == cuisine)
    if cursor:
        decoded = decode_cursor(cursor)
        if decoded:
            _, created_at = decoded
            q = q.where(Reel.created_at < created_at)

    q = q.limit(limit + 1)
    result = await db.execute(q)
    reels = result.scalars().all()

    has_more = len(reels) > limit
    reels = list(reels[:limit])

    # Batch fetch liked / saved sets for the current user
    liked_ids: set = set()
    saved_ids: set = set()
    if current_user and reels:
        reel_ids = [r.id for r in reels]
        lr = await db.execute(
            select(Like.reel_id).where(
                Like.user_id == current_user.id, Like.reel_id.in_(reel_ids)
            )
        )
        liked_ids = set(lr.scalars().all())
        sr = await db.execute(
            select(Save.reel_id).where(
                Save.user_id == current_user.id, Save.reel_id.in_(reel_ids)
            )
        )
        saved_ids = set(sr.scalars().all())

    data = [_build_reel_out(r, liked_ids, saved_ids) for r in reels]
    next_cursor = encode_cursor(reels[-1].id, reels[-1].created_at) if has_more else None
    return PaginatedReels(data=data, next_cursor=next_cursor, has_more=has_more)


async def get_reel_detail(
    db: AsyncSession, reel_id: uuid.UUID, current_user: User | None
) -> ReelDetailOut:
    result = await db.execute(
        select(Reel)
        .where(Reel.id == reel_id, Reel.status == "published")
        .options(
            selectinload(Reel.creator),
            selectinload(Reel.reel_restaurants).selectinload(ReelRestaurant.restaurant),
        )
    )
    reel = result.scalar_one_or_none()
    if not reel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reel not found")

    is_liked = False
    is_saved = False
    if current_user:
        lk = await db.execute(
            select(Like).where(Like.user_id == current_user.id, Like.reel_id == reel_id)
        )
        is_liked = lk.scalar_one_or_none() is not None
        sv = await db.execute(
            select(Save).where(Save.user_id == current_user.id, Save.reel_id == reel_id)
        )
        is_saved = sv.scalar_one_or_none() is not None

    comment_count_result = await db.execute(
        select(func.count()).where(Comment.reel_id == reel_id)
    )
    comment_count = comment_count_result.scalar() or 0

    restaurants = [
        RestaurantOut.model_validate(rr.restaurant) for rr in reel.reel_restaurants
    ]

    return ReelDetailOut(
        id=reel.id,
        title=reel.title,
        description=reel.description,
        video_url=reel.video_url,
        thumbnail_url=reel.thumbnail_url,
        duration_sec=reel.duration_sec,
        cuisine_tag=reel.cuisine_tag,
        view_count=reel.view_count,
        like_count=reel.like_count,
        save_count=reel.save_count,
        watch_time_seconds=reel.watch_time_seconds,
        is_liked=is_liked,
        is_saved=is_saved,
        creator=CreatorOut.model_validate(reel.creator),
        created_at=reel.created_at,
        comment_count=comment_count,
        restaurants=restaurants,
    )


async def toggle_like(
    db: AsyncSession, reel_id: uuid.UUID, user: User
) -> LikeResponse:
    reel_result = await db.execute(select(Reel).where(Reel.id == reel_id))
    reel = reel_result.scalar_one_or_none()
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")

    existing = await db.execute(
        select(Like).where(Like.user_id == user.id, Like.reel_id == reel_id)
    )
    like = existing.scalar_one_or_none()

    if like:
        await db.delete(like)
        reel.like_count = max(0, reel.like_count - 1)
        liked = False
    else:
        db.add(Like(user_id=user.id, reel_id=reel_id))
        reel.like_count += 1
        liked = True

    await db.commit()
    await db.refresh(reel)
    return LikeResponse(liked=liked, like_count=reel.like_count)


async def toggle_save(
    db: AsyncSession, reel_id: uuid.UUID, user: User
) -> SaveResponse:
    reel_result = await db.execute(select(Reel).where(Reel.id == reel_id))
    reel = reel_result.scalar_one_or_none()
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")

    existing = await db.execute(
        select(Save).where(Save.user_id == user.id, Save.reel_id == reel_id)
    )
    save = existing.scalar_one_or_none()

    if save:
        await db.delete(save)
        reel.save_count = max(0, reel.save_count - 1)
        saved = False
    else:
        db.add(Save(user_id=user.id, reel_id=reel_id))
        reel.save_count += 1
        saved = True

    await db.commit()
    await db.refresh(reel)
    return SaveResponse(saved=saved, save_count=reel.save_count)


async def record_watch_time(
    db: AsyncSession, reel_id: uuid.UUID, seconds: int
) -> WatchTimeResponse:
    """
    Atomically adds *seconds* to reel.watch_time_seconds and bumps view_count.
    Called by POST /api/v1/reels/{id}/watch from the frontend player.
    No authentication required — any viewer counts.
    """
    reel_result = await db.execute(
        select(Reel).where(Reel.id == reel_id, Reel.status == "published")
    )
    reel = reel_result.scalar_one_or_none()
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")

    reel.watch_time_seconds += seconds
    reel.view_count += 1
    await db.commit()
    await db.refresh(reel)

    return WatchTimeResponse(
        reel_id=reel.id,
        seconds_added=seconds,
        watch_time_seconds=reel.watch_time_seconds,
    )


async def create_reel(
    db: AsyncSession, current_user: User, data: ReelCreate
) -> ReelDetailOut:
    # 1. Create the Reel
    reel = Reel(
        creator_id=current_user.id,
        title=data.title,
        description=data.description,
        video_url=data.video_url,
        thumbnail_url=data.thumbnail_url,
        audio_url=data.audio_url,
        duration_sec=data.duration_sec,
        cuisine_tag=data.cuisine_tag,
        status="published",
    )
    db.add(reel)
    await db.flush()  # Generate reel.id
    
    # 2. Link to Restaurant
    if current_user.restaurant_id:
        reel_restaurant = ReelRestaurant(
            reel_id=reel.id,
            restaurant_id=current_user.restaurant_id
        )
        db.add(reel_restaurant)
        
    # 3. Add associated food items
    for item_data in data.food_items:
        food_item = FoodItem(
            reel_id=reel.id,
            name=item_data.name,
            description=item_data.description,
            price=item_data.price,
            currency=item_data.currency,
            image_url=item_data.image_url,
            category=item_data.category,
            is_veg=item_data.is_veg,
        )
        db.add(food_item)
        
    await db.commit()
    
    # 4. Fetch detail out using get_reel_detail
    return await get_reel_detail(db, reel.id, current_user)
