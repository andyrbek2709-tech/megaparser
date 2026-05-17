from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "social_engine",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.publish_task",
        "app.workers.analytics_task",
        "app.workers.strategy_task",
        "app.workers.generation_task",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "publish-due-posts": {
            "task": "app.workers.publish_task.publish_due_posts",
            "schedule": crontab(minute="*/5"),
        },
        "collect-pending-metrics": {
            "task": "app.workers.analytics_task.collect_all_pending_metrics",
            "schedule": crontab(minute=0),
        },
        "recalculate-all-strategies": {
            "task": "app.workers.strategy_task.recalculate_all_strategies",
            "schedule": crontab(hour=2, minute=0, day_of_week="monday"),
        },
    },
)
