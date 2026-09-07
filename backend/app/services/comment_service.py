"""
comment_service.py — CRUD operations for reel comments.

Endpoints:
  GET  /reels/{reel_id}/comments  — list newest comments for a reel
  POST /reels/{reel_id}/comments  — post a new comment (auth required)
  DELETE /reels/{reel_id}/comments/{comment_id} — delete own comment
"""
import uuid
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.social import Comment
from app.models.user import User
from app.schemas.social import CommentCreate, CommentOut


# CommentWithAuthor IS CommentOut — username/avatar_initial are already on the schema.
# This alias makes imports from comment_service cleaner.
CommentWithAuthor = CommentOut


async def list_comments(
    db: AsyncSession,
    reel_id: uuid.UUID,
    limit: int = 50,
) -> list[CommentWithAuthor]:
    """Return the latest `limit` comments for a reel, newest first."""
    result = await db.execute(
        select(Comment)
        .where(Comment.reel_id == reel_id)
        .options(selectinload(Comment.user))
        .order_by(Comment.created_at.desc())
        .limit(limit)
    )
    comments = result.scalars().all()
    # Reverse so oldest is first (chronological order for chat UI)
    comments = list(reversed(comments))
    return [
        CommentWithAuthor(
            id=c.id,
            reel_id=c.reel_id,
            user_id=c.user_id,
            body=c.body,
            created_at=c.created_at,
            username=c.user.username,
            avatar_initial=c.user.username[0].upper(),
        )
        for c in comments
    ]


async def create_comment(
    db: AsyncSession,
    reel_id: uuid.UUID,
    data: CommentCreate,
    current_user: User,
) -> CommentWithAuthor:
    """Create and persist a new comment. Returns it with author info."""
    body = data.body.strip()
    if not body:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Comment body cannot be empty.",
        )
    if len(body) > 500:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Comment must be 500 characters or fewer.",
        )

    comment = Comment(
        reel_id=reel_id,
        user_id=current_user.id,
        body=body,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    return CommentWithAuthor(
        id=comment.id,
        reel_id=comment.reel_id,
        user_id=comment.user_id,
        body=comment.body,
        created_at=comment.created_at,
        username=current_user.username,
        avatar_initial=current_user.username[0].upper(),
    )


async def delete_comment(
    db: AsyncSession,
    reel_id: uuid.UUID,
    comment_id: uuid.UUID,
    current_user: User,
) -> None:
    """Delete a comment. Only the author can delete their own comment."""
    result = await db.execute(
        select(Comment).where(
            Comment.id == comment_id,
            Comment.reel_id == reel_id,
        )
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found.",
        )
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments.",
        )
    await db.delete(comment)
    await db.commit()
