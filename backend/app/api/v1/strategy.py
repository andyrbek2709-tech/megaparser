import uuid

import structlog
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import DB, CurrentUser
from app.models.content_strategy import ContentStrategy
from app.models.post import Post
from app.models.analytics import PostMetrics
from app.services.ml.strategy_optimizer import StrategyOptimizer

logger = structlog.get_logger()
router = APIRouter()
optimizer = StrategyOptimizer()


@router.get("/{account_id}")
async def get_strategy(account_id: uuid.UUID, current_user: CurrentUser, db: DB) -> dict:
    result = await db.execute(
        select(ContentStrategy).where(
            ContentStrategy.social_account_id == account_id,
            ContentStrategy.user_id == current_user.id,
            ContentStrategy.is_active == True,
        ).order_by(ContentStrategy.created_at.desc()).limit(1)
    )
    strategy = result.scalar_one_or_none()
    if not strategy:
        return {"strategy_data": optimizer._default_strategy(), "is_default": True}
    return {"id": str(strategy.id), "strategy_data": strategy.strategy_data, "model_version": strategy.model_version, "created_at": strategy.created_at.isoformat()}


@router.post("/{account_id}/recalculate")
async def recalculate_strategy(account_id: uuid.UUID, current_user: CurrentUser, db: DB) -> dict:
    from app.workers.strategy_task import recalculate_strategy as recalc_task
    recalc_task.delay(str(current_user.id), str(account_id))
    return {"message": "Strategy recalculation started"}


@router.get("/{account_id}/history")
async def strategy_history(account_id: uuid.UUID, current_user: CurrentUser, db: DB) -> list[dict]:
    result = await db.execute(
        select(ContentStrategy).where(
            ContentStrategy.social_account_id == account_id,
            ContentStrategy.user_id == current_user.id,
        ).order_by(ContentStrategy.created_at.desc()).limit(10)
    )
    strategies = result.scalars().all()
    return [{"id": str(s.id), "created_at": s.created_at.isoformat(), "model_version": s.model_version, "is_active": s.is_active} for s in strategies]
