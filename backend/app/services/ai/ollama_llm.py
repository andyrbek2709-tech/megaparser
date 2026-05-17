# TODO: Implement Ollama backend when needed
from app.services.ai.base_llm import BaseLLM


class OllamaLLM(BaseLLM):
    async def complete(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> str:
        raise NotImplementedError("Ollama integration not yet implemented")

    async def embed(self, text: str) -> list[float]:
        raise NotImplementedError("Ollama integration not yet implemented")
