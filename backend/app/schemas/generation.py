import uuid

from pydantic import BaseModel


class GenerationRequest(BaseModel):
    topic: str
    platform: str
    tone: str
    style_hints: list[str] = []
    account_id: uuid.UUID | None = None


class GeneratedContent(BaseModel):
    text: str
    image_prompt: str
    image_url: str | None
    hashtags: list[str]
    estimated_engagement: float


class BatchGenerationRequest(BaseModel):
    account_id: uuid.UUID
    topics: list[str]
    platform: str
    tone: str


class RegenerateRequest(BaseModel):
    regenerate_text: bool = True
    regenerate_image: bool = True
