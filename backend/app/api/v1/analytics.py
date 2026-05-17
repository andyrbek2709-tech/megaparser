import uuid
from datetime import datetime, timedelta, timezone

import structlog
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select, text

from app.api.deps import DB, CurrentUser
from app.models.analytics import PostMetrics
from app.models.post import Post
from app.schemas.analytics import BestTimeSlot, EngagementTrendPoint, MetricsResponse, OverviewStats

logger = structlog.get_logger()
router = APIRouter()


@router.get("/overview", response_model=OverviewStats)
async def overview(current_user: CurrentUser, db: DB) -> dict:
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    posts_result = await db.execute(
        select(func.count(Post.id)).where(Post.user_id == current_user.id, Post.created_at >= week_ago)
    )
    total_posts_week = posts_result.scalar() or 0

    avg_result = await db.execute(
        select(func.avg(PostMetrics.engagement_rate))
        .join(Post, PostMetrics.post_id == Post.id)
        .where(Post.user_id == current_user.id)
    )
    avg_engagement = float(avg_result.scalar() or 0)

    return {
        "total_posts_week": total_posts_week,
        "avg_engagement_rate": avg_engagement,
        "best_post_id": None,
        "predicted_next_engagement": avg_engagement * 1.1,
    }


@router.get("/engagement-trend", response_model=list[EngagementTrendPoint])
async def engagement_trend(
    current_user: CurrentUser,
    db: DB,
    account_id: uuid.UUID | None = Query(None),
    days: int = Query(30, le=90),
) -> list[dict]:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    q = (
        select(
            func.date(PostMetrics.collected_at).label("date"),
            func.avg(PostMetrics.engagement_rate).label("avg_engagement_rate"),
            func.count(PostMetrics.id).label("post_count"),
        )
        .join(Post, PostMetrics.post_id == Post.id)
        .where(Post.user_id == current_user.id, PostMetrics.collected_at >= since)
        .group_by(func.date(PostMetrics.collected_at))
        .order_by(func.date(PostMetrics.collected_at))
    )
    result = await db.execute(q)
    return [{"date": str(row.date), "avg_engagement_rate": float(row.avg_engagement_rate or 0), "post_count": row.post_count} for row in result]


@router.get("/best-times", response_model=list[BestTimeSlot])
async def best_times(current_user: CurrentUser, db: DB) -> list[dict]:
    q = (
        select(
            func.extract("dow", Post.published_at).label("day"),
            func.extract("hour", Post.published_at).label("hour"),
            func.avg(PostMetrics.engagement_rate).label("avg_engagement"),
        )
        .join(PostMetrics, PostMetrics.post_id == Post.id)
        .where(Post.user_id == current_user.id, Post.published_at.isnot(None))
        .group_by(func.extract("dow", Post.published_at), func.extract("hour", Post.published_at))
    )
    result = await db.execute(q)
    return [{"day": int(row.day or 0), "hour": int(row.hour or 0), "avg_engagement": float(row.avg_engagement or 0)} for row in result]


@router.get("/top-posts")
async def top_posts(current_user: CurrentUser, db: DB, limit: int = Query(10, le=50)) -> list[dict]:
    q = (
        select(Post, func.max(PostMetrics.engagement_rate).label("max_er"))
        .join(PostMetrics, PostMetrics.post_id == Post.id)
        .where(Post.user_id == current_user.id)
        .group_by(Post.id)
        .order_by(func.max(PostMetrics.engagement_rate).desc())
        .limit(limit)
    )
    result = await db.execute(q)
    return [
        {
            "id": str(row.Post.id),
            "content_text": row.Post.content_text,
            "image_url": row.Post.image_url,
            "engagement_rate": float(row.max_er or 0),
            "published_at": row.Post.published_at.isoformat() if row.Post.published_at else None,
        }
        for row in result
    ]


@router.get("/content-performance")
async def content_performance(current_user: CurrentUser, db: DB) -> dict:
    result = await db.execute(
        select(
            Post.generation_params["platform"].astext.label("platform"),
            func.avg(PostMetrics.engagement_rate).label("avg_er"),
            func.count(Post.id).label("count"),
        )
        .join(PostMetrics, PostMetrics.post_id == Post.id)
        .where(Post.user_id == current_user.id)
        .group_by(Post.generation_params["platform"].astext)
    )
    return {"by_platform": [{"platform": r.platform, "avg_engagement": float(r.avg_er or 0), "count": r.count} for r in result]}


@router.post("/export")
async def export_csv(current_user: CurrentUser, db: DB) -> StreamingResponse:
    import csv
    import io

    result = await db.execute(
        select(Post, PostMetrics)
        .join(PostMetrics, PostMetrics.post_id == Post.id, isouter=True)
        .where(Post.user_id == current_user.id)
        .order_by(Post.created_at.desc())
    )
    rows = result.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["post_id", "status", "content_text", "published_at", "likes", "comments", "shares", "saves", "reach", "engagement_rate"])
    for post, metrics in rows:
        writer.writerow([
            str(post.id), post.status, (post.content_text or "")[:100],
            post.published_at.isoformat() if post.published_at else "",
            metrics.likes if metrics else 0,
            metrics.comments if metrics else 0,
            metrics.shares if metrics else 0,
            metrics.saves if metrics else 0,
            metrics.reach if metrics else 0,
            metrics.engagement_rate if metrics else 0,
        ])

    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=analytics.csv"})
