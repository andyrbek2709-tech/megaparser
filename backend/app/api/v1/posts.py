import uuid
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from app.api.deps import DB, CurrentUser
from app.models.post import Post
from app.models.analytics import PostMetrics
from app.schemas.post import PostCreate, PostResponse, PostSchedule, PostUpdate
from app.schemas.analytics import MetricsResponse

logger = structlog.get_logger()
router = APIRouter()


@router.get("", response_model=list[PostResponse])
async def list_posts(
    current_user: CurrentUser,
    db: DB,
    status: str | None = Query(None),
    account_id: uuid.UUID | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
) -> list[Post]:
    q = select(Post).where(Post.user_id == current_user.id)
    if status:
        q = q.where(Post.status == status)
    if account_id:
        q = q.where(Post.social_account_id == account_id)
    q = q.order_by(Post.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(q)
    return list(result.scalars().all())


@router.post("", response_model=PostResponse, status_code=201)
async def create_post(data: PostCreate, current_user: CurrentUser, db: DB) -> Post:
    post = Post(
        user_id=current_user.id,
        social_account_id=data.social_account_id,
        content_text=data.content_text,
        image_url=data.image_url,
        scheduled_at=data.scheduled_at,
        generation_params=data.generation_params,
        status="scheduled" if data.scheduled_at else "draft",
    )
    db.add(post)
    await db.flush()
    await db.refresh(post)
    return post


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: uuid.UUID, current_user: CurrentUser, db: DB) -> Post:
    result = await db.execute(select(Post).where(Post.id == post_id, Post.user_id == current_user.id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Post not found"})
    return post


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(post_id: uuid.UUID, data: PostUpdate, current_user: CurrentUser, db: DB) -> Post:
    result = await db.execute(select(Post).where(Post.id == post_id, Post.user_id == current_user.id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Post not found"})
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(post, field, value)
    await db.flush()
    await db.refresh(post)
    return post


@router.delete("/{post_id}", status_code=204)
async def delete_post(post_id: uuid.UUID, current_user: CurrentUser, db: DB) -> None:
    result = await db.execute(select(Post).where(Post.id == post_id, Post.user_id == current_user.id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Post not found"})
    await db.delete(post)


@router.post("/{post_id}/publish-now", response_model=PostResponse)
async def publish_now(post_id: uuid.UUID, current_user: CurrentUser, db: DB) -> Post:
    result = await db.execute(select(Post).where(Post.id == post_id, Post.user_id == current_user.id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Post not found"})
    from app.workers.publish_task import publish_scheduled_post
    publish_scheduled_post.delay(str(post_id))
    return post


@router.post("/{post_id}/schedule", response_model=PostResponse)
async def schedule_post(post_id: uuid.UUID, data: PostSchedule, current_user: CurrentUser, db: DB) -> Post:
    result = await db.execute(select(Post).where(Post.id == post_id, Post.user_id == current_user.id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Post not found"})
    post.scheduled_at = data.scheduled_at
    post.status = "scheduled"
    await db.flush()
    await db.refresh(post)
    return post


@router.get("/{post_id}/metrics", response_model=list[MetricsResponse])
async def post_metrics(post_id: uuid.UUID, current_user: CurrentUser, db: DB) -> list[PostMetrics]:
    result = await db.execute(select(Post).where(Post.id == post_id, Post.user_id == current_user.id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Post not found"})
    m_result = await db.execute(select(PostMetrics).where(PostMetrics.post_id == post_id).order_by(PostMetrics.collected_at))
    return list(m_result.scalars().all())
