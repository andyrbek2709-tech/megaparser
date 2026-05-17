import asyncio
import structlog
from app.workers.celery_app import celery_app

logger = structlog.get_logger()


@celery_app.task(name="app.workers.analytics_task.collect_post_metrics")
def collect_post_metrics(post_id: str) -> dict:
    async def _run():
        from app.database import AsyncSessionLocal
        from app.models.post import Post
        from app.services.analytics.collector import collect_metrics_for_post
        from sqlalchemy import select

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Post).where(Post.id == post_id))
            post = result.scalar_one_or_none()
            if not post:
                return {"error": "Post not found"}
            metrics = await collect_metrics_for_post(post, db)
            await db.commit()
            return {"collected": metrics is not None}

    return asyncio.run(_run())


@celery_app.task(name="app.workers.analytics_task.collect_all_pending_metrics")
def collect_all_pending_metrics() -> dict:
    async def _run():
        from datetime import datetime, timedelta, timezone
        from app.database import AsyncSessionLocal
        from app.models.post import Post
        from sqlalchemy import select

        async with AsyncSessionLocal() as db:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
            result = await db.execute(
                select(Post).where(Post.status == "published", Post.published_at >= cutoff - timedelta(days=7))
            )
            posts = result.scalars().all()
            for post in posts:
                collect_post_metrics.delay(str(post.id))
            return {"dispatched": len(posts)}

    return asyncio.run(_run())
