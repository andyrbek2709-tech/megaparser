import asyncio
import structlog
from openai import AsyncOpenAI

from app.config import settings
from app.services.ai.base_llm import BaseLLM

logger = structlog.get_logger()


class OpenAILLM(BaseLLM):
    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_TEXT_MODEL

    async def complete(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> str:
        for attempt in range(3):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    max_tokens=max_tokens,
                    temperature=0.8,
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                if attempt == 2:
                    raise
                await asyncio.sleep(2 ** attempt)
                logger.warning("llm_retry", attempt=attempt, error=str(e))
        return ""

    async def embed(self, text: str) -> list[float]:
        response = await self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=text[:8000],
        )
        return response.data[0].embedding
