import asyncio
import structlog
from celery import shared_task

from app.workers.celery_app import celery_app

logger = structlog.get_logger()


@celery_app.task(bind=True, max_retries=3, name="app.workers.publish_task.publish_scheduled_post")
def publish_scheduled_post(self, post_id: str) -> dict:
    async def _publish():
        from app.database import AsyncSessionLocal
        from app.models.post import Post
        from app.models.social_account import SocialAccount
        from sqlalchemy import select
        from datetime import datetime, timezone

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Post).where(Post.id == post_id))
            post = result.scalar_one_or_none()
            if not post:
                return {"error": "Post not found"}
            if post.status == "published":
                return {"status": "already_published"}

            acc_result = await db.execute(select(SocialAccount).where(SocialAccount.id == post.social_account_id))
            account = acc_result.scalar_one_or_none()
            if not account:
                post.status = "failed"
                post.error_message = "Social account not found"
                await db.commit()
                return {"error": "Account not found"}

            try:
                if account.platform == "instagram":
                    from app.services.social.instagram import InstagramClient
                    client = InstagramClient()
                    platform_id = await client.publish_photo(account, post.image_url or "", post.content_text or "")
                else:
                    raise ValueError(f"Unsupported platform: {account.platform}")

                post.platform_post_id = platform_id
                post.status = "published"
                post.published_at = datetime.now(timezone.utc)
                await db.commit()
                collect_post_metrics.apply_async(args=[post_id], countdown=3600)
                return {"status": "published", "platform_post_id": platform_id}
            except Exception as e:
                post.status = "failed"
                post.error_message = str(e)
                await db.commit()
                raise self.retry(exc=e, countdown=2 ** self.request.retries * 60)

    return asyncio.run(_publish())


@celery_app.task(name="app.workers.publish_task.publish_due_posts")
def publish_due_posts() -> dict:
    async def _run():
        from app.database import AsyncSessionLocal
        from app.models.post import Post
        from sqlalchemy import select
        from datetime import datetime, timezone

        async with AsyncSessionLocal() as db:
            now = datetime.now(timezone.utc)
            result = await db.execute(
                select(Post).where(Post.status == "scheduled", Post.scheduled_at <= now)
            )
            posts = result.scalars().all()
            for post in posts:
                publish_scheduled_post.delay(str(post.id))
            return {"dispatched": len(posts)}

    return asyncio.run(_run())


from app.workers.analytics_task import collect_post_metrics  # noqa: E402
