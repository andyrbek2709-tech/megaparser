import re
import structlog

from app.schemas.generation import GeneratedContent
from app.services.ai.base_image import BaseImageGenerator
from app.services.ai.base_llm import BaseLLM
from app.services.ai.dalle_image import DalleImageGenerator
from app.services.ai.openai_llm import OpenAILLM

logger = structlog.get_logger()

PLATFORM_CONSTRAINTS = {
    "instagram": {"max_chars": 2200, "optimal_hashtags": 10, "best_practices": "Use emojis, line breaks for readability, 10 relevant hashtags"},
    "youtube": {"max_chars": 5000, "optimal_hashtags": 5, "best_practices": "SEO-optimized title and description, include timestamps if applicable"},
    "reddit": {"max_chars": 40000, "optimal_hashtags": 0, "best_practices": "Conversational tone, no hashtags, start with an engaging hook"},
}

TONE_PROMPTS = {
    "professional": "authoritative, informative, polished",
    "casual": "friendly, conversational, relatable",
    "humorous": "witty, playful, entertaining",
    "inspirational": "motivating, uplifting, empowering",
}


class ContentGenerator:
    def __init__(self, llm: BaseLLM | None = None, image_gen: BaseImageGenerator | None = None) -> None:
        self.llm = llm or OpenAILLM()
        self.image_gen = image_gen or DalleImageGenerator()

    async def generate_post(
        self,
        topic: str,
        platform: str,
        tone: str,
        style_hints: list[str],
        account_history: list[dict] | None = None,
        strategy: dict | None = None,
        regenerate_text: bool = True,
        regenerate_image: bool = True,
        existing_text: str | None = None,
        existing_image_url: str | None = None,
    ) -> GeneratedContent:
        constraints = PLATFORM_CONSTRAINTS.get(platform, PLATFORM_CONSTRAINTS["instagram"])
        tone_desc = TONE_PROMPTS.get(tone, tone)

        history_context = ""
        if account_history:
            top_posts = account_history[:3]
            history_context = f"\n\nAccount's top performing posts for style reference:\n" + "\n---\n".join(
                p.get("text", "")[:200] for p in top_posts if p.get("text")
            )

        if regenerate_text:
            system = (
                f"You are a social media content expert for {platform}. "
                f"Platform constraints: max {constraints['max_chars']} chars, "
                f"use {constraints['optimal_hashtags']} hashtags, {constraints['best_practices']}. "
                f"Tone: {tone_desc}. "
                f"Style: {', '.join(style_hints) if style_hints else 'versatile'}."
                f"{history_context}"
            )
            user = f"Create a {platform} post about: {topic}"
            if strategy:
                user += f"\nStrategy guidance: {strategy.get('recommended_tone', '')} tone, topics: {strategy.get('recommended_topics', [])}"

            text = await self.llm.complete(system, user, max_tokens=800)
            hashtags = self._extract_hashtags(text)
        else:
            text = existing_text or ""
            hashtags = self._extract_hashtags(text)

        if regenerate_image:
            image_prompt_system = "You are a visual art director. Create a detailed DALL-E image prompt."
            image_prompt_user = (
                f"Create an image prompt for a {platform} post about '{topic}'. "
                f"Style: {', '.join(style_hints) if style_hints else 'modern, clean'}. "
                f"Tone: {tone_desc}. Keep it under 200 words."
            )
            image_prompt = await self.llm.complete(image_prompt_system, image_prompt_user, max_tokens=200)
            image_url = await self.image_gen.generate(image_prompt)
        else:
            image_prompt = ""
            image_url = existing_image_url

        estimated_engagement = self._estimate_engagement(text, platform, style_hints)

        return GeneratedContent(
            text=text,
            image_prompt=image_prompt,
            image_url=image_url,
            hashtags=hashtags,
            estimated_engagement=estimated_engagement,
        )

    def _extract_hashtags(self, text: str) -> list[str]:
        return re.findall(r"#\w+", text)

    def _estimate_engagement(self, text: str, platform: str, style_hints: list[str]) -> float:
        score = 0.05
        if len(text) > 100:
            score += 0.01
        if self._extract_hashtags(text):
            score += 0.01
        if any(h in ["bright colors", "people", "lifestyle"] for h in style_hints):
            score += 0.01
        return round(min(score, 0.15), 4)
