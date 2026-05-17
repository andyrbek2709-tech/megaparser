import uuid
from datetime import datetime

from pydantic import BaseModel


class PostCreate(BaseModel):
    social_account_id: uuid.UUID
    content_text: str | None = None
    image_url: str | None = None
    scheduled_at: datetime | None = None
    generation_params: dict = {}


class PostUpdate(BaseModel):
    content_text: str | None = None
    image_url: str | None = None
    scheduled_at: datetime | None = None
    status: str | None = None


class PostSchedule(BaseModel):
    scheduled_at: datetime


class PostResponse(BaseModel):
    id: uuid.UUID
    social_account_id: uuid.UUID | None
    user_id: uuid.UUID | None
    status: str
    content_text: str | None
    image_url: str | None
    scheduled_at: datetime | None
    published_at: datetime | None
    generation_params: dict
    created_at: datetime
    error_message: str | None

    model_config = {"from_attributes": True}
