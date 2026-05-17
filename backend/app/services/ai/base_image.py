from abc import ABC, abstractmethod


class BaseImageGenerator(ABC):
    @abstractmethod
    async def generate(self, prompt: str, size: str = "1024x1024") -> str:
        pass
