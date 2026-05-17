import asyncio
import structlog
from app.workers.celery_app import celery_app

logger = structlog.get_logger()


@celery_app.task(name="app.workers.strategy_task.recalculate_strategy")
def recalculate_strategy(user_id: str, social_account_id: str) -> dict:
    async def _run():
        from app.database import AsyncSessionLocal
        from app.models.post import Post
        from app.models.analytics import PostMetrics
        from app.models.content_strategy import ContentStrategy
        from app.services.ml.strategy_optimizer import StrategyOptimizer
        from sqlalchemy import select

        async with AsyncSessionLocal() as db:
            posts_result = await db.execute(
                select(Post).where(Post.social_account_id == social_account_id, Post.status == "published").limit(100)
            )
            posts = posts_result.scalars().all()
            posts_history = [{"content_text": p.content_text, "generation_params": p.generation_params, "published_at": p.published_at.isoformat() if p.published_at else None} for p in posts]

            metrics_result = await db.execute(
                select(PostMetrics).join(Post, PostMetrics.post_id == Post.id).where(Post.social_account_id == social_account_id).limit(200)
            )
            metrics = metrics_result.scalars().all()
            metrics_history = [{"engagement_rate": m.engagement_rate, "day_of_week": m.collected_at.weekday(), "hour_of_day": m.collected_at.hour} for m in metrics]

            optimizer = StrategyOptimizer()
            strategy_data = optimizer.generate_weekly_plan(social_account_id, posts_history, metrics_history)

            await db.execute(
                ContentStrategy.__table__.update()
                .where(ContentStrategy.social_account_id == social_account_id)
                .values(is_active=False)
            )
            new_strategy = ContentStrategy(
                user_id=user_id,
                social_account_id=social_account_id,
                strategy_data=strategy_data,
                model_version="1.0",
                is_active=True,
            )
            db.add(new_strategy)
            await db.commit()
            return {"status": "recalculated", "strategy_id": str(new_strategy.id)}

    return asyncio.run(_run())


@celery_app.task(name="app.workers.strategy_task.recalculate_all_strategies")
def recalculate_all_strategies() -> dict:
    async def _run():
        from app.database import AsyncSessionLocal
        from app.models.social_account import SocialAccount
        from sqlalchemy import select

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(SocialAccount).where(SocialAccount.is_active == True))
            accounts = result.scalars().all()
            for account in accounts:
                recalculate_strategy.delay(str(account.user_id), str(account.id))
            return {"dispatched": len(accounts)}

    return asyncio.run(_run())
