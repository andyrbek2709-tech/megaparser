import asyncio
import structlog
from openai import AsyncOpenAI

from app.config import settings
from app.services.ai.base_image import BaseImageGenerator

logger = structlog.get_logger()


class DalleImageGenerator(BaseImageGenerator):
    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate(self, prompt: str, size: str | None = None) -> str:
        size = size or settings.OPENAI_IMAGE_SIZE
        for attempt in range(3):
            try:
                response = await self.client.images.generate(
                    model=settings.OPENAI_IMAGE_MODEL,
                    prompt=prompt[:4000],
                    size=size,  # type: ignore
                    quality="standard",
                    n=1,
                )
                return response.data[0].url or ""
            except Exception as e:
                if attempt == 2:
                    raise
                await asyncio.sleep(2 ** attempt)
                logger.warning("dalle_retry", attempt=attempt, error=str(e))
        return ""
