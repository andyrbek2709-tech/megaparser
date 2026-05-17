import uuid
from datetime import datetime

from pydantic import BaseModel


class MetricsResponse(BaseModel):
    id: uuid.UUID
    post_id: uuid.UUID | None
    collected_at: datetime
    likes: int
    comments: int
    shares: int
    saves: int
    reach: int
    impressions: int
    watch_through_rate: float | None
    engagement_rate: float

    model_config = {"from_attributes": True}


class EngagementTrendPoint(BaseModel):
    date: str
    avg_engagement_rate: float
    post_count: int


class BestTimeSlot(BaseModel):
    day: int
    hour: int
    avg_engagement: float


class OverviewStats(BaseModel):
    total_posts_week: int
    avg_engagement_rate: float
    best_post_id: uuid.UUID | None
    predicted_next_engagement: float
