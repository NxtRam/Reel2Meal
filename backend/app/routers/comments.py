"""
routers/comments.py — Comment endpoints nested under /reels/{reel_id}/comments.

GET  /api/v1/reels/{reel_id}/comments           — list (public)
POST /api/v1/reels/{reel_id}/comments           — create (auth required)
DELETE /api/v1/reels/{reel_id}/comments/{id}    — delete own comment
"""
import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_current_user, get_optional_user
from app.models.user import User
from app.schemas.social import CommentCreate, CommentOut
from app.services import comment_service
from app.services.comment_service import CommentWithAuthor

router = APIRouter(
    prefix="/reels/{reel_id}/comments",
    tags=["Comments"],
    redirect_slashes=False,   # prevents 307 redirect stripping Authorization header
)


@router.get("/", response_model=list[CommentWithAuthor])
async def list_comments(
    reel_id: uuid.UUID,
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _: User | None = Depends(get_optional_user),  # auth optional — public read
):
    """
    List the latest comments for a reel (chronological order, oldest first).
    No authentication required — comments are publicly readable.
    """
    return await comment_service.list_comments(db, reel_id, limit=limit)


@router.post("/", response_model=CommentWithAuthor, status_code=status.HTTP_201_CREATED)
async def create_comment(
    reel_id: uuid.UUID,
    data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Post a new comment on a reel.
    Requires authentication. Max 500 characters.
    """
    return await comment_service.create_comment(db, reel_id, data, current_user)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    reel_id: uuid.UUID,
    comment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a comment. Only the original author can delete their comment."""
    await comment_service.delete_comment(db, reel_id, comment_id, current_user)
