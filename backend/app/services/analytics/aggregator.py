from datetime import datetime, timedelta, timezone
import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import PostMetrics
from app.models.post import Post

logger = structlog.get_logger()


async def get_account_avg_engagement(account_id, db: AsyncSession, days: int = 7) -> float:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(func.avg(PostMetrics.engagement_rate))
        .join(Post, PostMetrics.post_id == Post.id)
        .where(Post.social_account_id == account_id, PostMetrics.collected_at >= since)
    )
    return float(result.scalar() or 0)


async def get_post_frequency(account_id, db: AsyncSession, days: int = 7) -> float:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(func.count(Post.id))
        .where(Post.social_account_id == account_id, Post.created_at >= since)
    )
    return float(result.scalar() or 0)
