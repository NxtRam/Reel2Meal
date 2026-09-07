"""
Phase 2 Feed Service
====================
Scoring formula: score = like_count * 3 + save_count * 5 + watch_time_seconds * 1

Weights are imported from schemas.reel so they stay in sync with the
computed_field `feed_score` exposed on ReelOut.

Pagination strategy
-------------------
We use *score-based keyset pagination* instead of timestamp-based cursors so
that reels don't jump around when scores change between page loads:

    cursor encodes  (score_at_fetch, reel_id)
    next page WHERE score < cursor_score
               OR  (score = cursor_score AND id < cursor_id)   -- tie-break

This gives a stable, gap-free result set even under concurrent score updates.
"""

import uuid

from sqlalchemy import select, case, literal_column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import and_, or_

from app.models.reel import Reel
from app.models.social import Like, Save
from app.models.user import User
from app.schemas.reel import (
    PaginatedReels,
    ReelOut,
    CreatorOut,
    SCORE_WEIGHT_LIKES,
    SCORE_WEIGHT_SAVES,
    SCORE_WEIGHT_WATCH_TIME,
)
from app.utils.score_cursor import encode_score_cursor, decode_score_cursor


MAX_LIMIT = 20

# SQLAlchemy expression for the ranking score — used in ORDER BY and WHERE
_score_expr = (
    Reel.like_count * SCORE_WEIGHT_LIKES
    + Reel.save_count * SCORE_WEIGHT_SAVES
    + Reel.watch_time_seconds * SCORE_WEIGHT_WATCH_TIME
)


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


async def get_feed(
    db: AsyncSession,
    current_user: User,
    cursor: str | None,
    limit: int,
) -> PaginatedReels:
    """
    Return a ranked feed for *current_user*.

    Phase 2 ranking formula
    -----------------------
    score = like_count * 3 + save_count * 5 + watch_time_seconds * 1

    Pages are keyset-paginated on (score DESC, id DESC) so results are
    stable across concurrent score updates.
    """
    limit = min(limit, MAX_LIMIT)

    # Base query — score expression applied once
    q = (
        select(Reel)
        .where(Reel.status == "published")
        .options(selectinload(Reel.creator))
        .order_by(_score_expr.desc(), Reel.id.desc())
    )

    # Apply cursor filter for pages > 1
    if cursor:
        decoded = decode_score_cursor(cursor)
        if decoded:
            cursor_score, cursor_id = decoded
            q = q.where(
                or_(
                    _score_expr < cursor_score,
                    and_(
                        _score_expr == cursor_score,
                        Reel.id < cursor_id,
                    ),
                )
            )

    q = q.limit(limit + 1)
    result = await db.execute(q)
    reels = list(result.scalars().all())

    has_more = len(reels) > limit
    reels = reels[:limit]

    # Batch-fetch liked / saved sets for this user
    liked_ids: set = set()
    saved_ids: set = set()
    if reels:
        reel_ids = [r.id for r in reels]
        lr = await db.execute(
            select(Like.reel_id).where(
                Like.user_id == current_user.id,
                Like.reel_id.in_(reel_ids),
            )
        )
        liked_ids = set(lr.scalars().all())
        sr = await db.execute(
            select(Save.reel_id).where(
                Save.user_id == current_user.id,
                Save.reel_id.in_(reel_ids),
            )
        )
        saved_ids = set(sr.scalars().all())

    data = [_build_reel_out(r, liked_ids, saved_ids) for r in reels]

    # Build next cursor from the last reel's computed score
    next_cursor = None
    if has_more:
        last = reels[-1]
        last_score = (
            last.like_count * SCORE_WEIGHT_LIKES
            + last.save_count * SCORE_WEIGHT_SAVES
            + last.watch_time_seconds * SCORE_WEIGHT_WATCH_TIME
        )
        next_cursor = encode_score_cursor(last_score, last.id)

    return PaginatedReels(data=data, next_cursor=next_cursor, has_more=has_more)
