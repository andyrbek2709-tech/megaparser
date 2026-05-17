import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.post import Post
from app.models.analytics import PostMetrics
from app.models.social_account import SocialAccount

logger = structlog.get_logger()


async def collect_metrics_for_post(post: Post, db: AsyncSession) -> PostMetrics | None:
    if not post.platform_post_id or not post.social_account_id:
        return None

    result = await db.execute(select(SocialAccount).where(SocialAccount.id == post.social_account_id))
    account = result.scalar_one_or_none()
    if not account:
        return None

    try:
        if account.platform == "instagram":
            from app.services.social.instagram import InstagramClient
            client = InstagramClient()
            raw = await client.get_post_insights(account, post.platform_post_id)
        elif account.platform == "youtube":
            from app.services.social.youtube import YouTubeClient
            client = YouTubeClient()
            raw = await client.get_post_insights(account, post.platform_post_id)
        elif account.platform == "reddit":
            from app.services.social.reddit import RedditClient
            client = RedditClient()
            raw = await client.get_post_insights(account, post.platform_post_id)
        else:
            return None
    except Exception as e:
        logger.error("metrics_collection_failed", post_id=str(post.id), error=str(e))
        return None

    metrics = PostMetrics(
        post_id=post.id,
        likes=raw.get("likes", 0),
        comments=raw.get("comments", 0),
        shares=raw.get("shares", 0),
        saves=raw.get("saves", 0),
        reach=raw.get("reach", 0),
        impressions=raw.get("impressions", raw.get("reach", 0)),
        raw_data=raw,
    )
    db.add(metrics)
    await db.flush()
    return metrics
