import uuid

import structlog
from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.deps import DB, CurrentUser
from app.models.post import Post
from app.models.social_account import SocialAccount
from app.schemas.generation import BatchGenerationRequest, GeneratedContent, GenerationRequest, RegenerateRequest
from app.services.ai.content_generator import ContentGenerator

logger = structlog.get_logger()
router = APIRouter()
generator = ContentGenerator()
limiter = Limiter(key_func=get_remote_address)


@router.post("/generate", response_model=GeneratedContent)
@limiter.limit("20/hour")
async def generate_content(request: Request, data: GenerationRequest, current_user: CurrentUser, db: DB) -> GeneratedContent:
    account_history = None
    if data.account_id:
        result = await db.execute(
            select(Post).where(
                Post.user_id == current_user.id,
                Post.social_account_id == data.account_id,
                Post.status == "published",
            ).order_by(Post.published_at.desc()).limit(10)
        )
        posts = result.scalars().all()
        account_history = [{"text": p.content_text, "params": p.generation_params} for p in posts]

    content = await generator.generate_post(
        topic=data.topic,
        platform=data.platform,
        tone=data.tone,
        style_hints=data.style_hints,
        account_history=account_history,
    )
    return content


@router.post("/regenerate/{post_id}", response_model=GeneratedContent)
@limiter.limit("20/hour")
async def regenerate_post(request: Request, post_id: uuid.UUID, data: RegenerateRequest, current_user: CurrentUser, db: DB) -> GeneratedContent:
    result = await db.execute(select(Post).where(Post.id == post_id, Post.user_id == current_user.id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Post not found"})

    params = post.generation_params or {}
    content = await generator.generate_post(
        topic=params.get("topic", ""),
        platform=params.get("platform", "instagram"),
        tone=params.get("tone", "casual"),
        style_hints=params.get("style_hints", []),
        regenerate_text=data.regenerate_text,
        regenerate_image=data.regenerate_image,
        existing_text=post.content_text if not data.regenerate_text else None,
        existing_image_url=post.image_url if not data.regenerate_image else None,
    )
    return content


@router.post("/batch", response_model=list[GeneratedContent])
@limiter.limit("5/hour")
async def batch_generate(request: Request, data: BatchGenerationRequest, current_user: CurrentUser, db: DB) -> list[GeneratedContent]:
    results = []
    for topic in data.topics[:7]:
        content = await generator.generate_post(
            topic=topic,
            platform=data.platform,
            tone=data.tone,
            style_hints=[],
        )
        results.append(content)
    return results
