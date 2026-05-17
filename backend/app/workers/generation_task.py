import asyncio
import structlog
from app.workers.celery_app import celery_app

logger = structlog.get_logger()


@celery_app.task(name="app.workers.generation_task.generate_content_async")
def generate_content_async(post_id: str, generation_params: dict) -> dict:
    async def _run():
        from app.database import AsyncSessionLocal
        from app.models.post import Post
        from app.services.ai.content_generator import ContentGenerator
        from sqlalchemy import select

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Post).where(Post.id == post_id))
            post = result.scalar_one_or_none()
            if not post:
                return {"error": "Post not found"}

            generator = ContentGenerator()
            content = await generator.generate_post(
                topic=generation_params.get("topic", ""),
                platform=generation_params.get("platform", "instagram"),
                tone=generation_params.get("tone", "casual"),
                style_hints=generation_params.get("style_hints", []),
            )
            post.content_text = content.text
            post.image_url = content.image_url
            post.generation_params = generation_params
            await db.commit()
            return {"status": "generated", "post_id": post_id}

    return asyncio.run(_run())
