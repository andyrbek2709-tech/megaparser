# TODO: Implement Stable Diffusion when needed
from app.services.ai.base_image import BaseImageGenerator


class StableDiffusionGenerator(BaseImageGenerator):
    async def generate(self, prompt: str, size: str = "1024x1024") -> str:
        raise NotImplementedError("Stable Diffusion integration not yet implemented")
