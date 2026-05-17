from abc import ABC, abstractmethod


class BaseLLM(ABC):
    @abstractmethod
    async def complete(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> str:
        pass

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        pass
