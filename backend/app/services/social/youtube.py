import structlog
from app.models.social_account import SocialAccount
from app.services.social.base_platform import BasePlatform

logger = structlog.get_logger()


class YouTubeClient(BasePlatform):
    async def publish_photo(self, account: SocialAccount, image_url: str, caption: str) -> str:
        raise NotImplementedError("YouTube does not support photo posts")

    async def get_post_insights(self, account: SocialAccount, post_id: str) -> dict:
        from app.services.security import decrypt_token
        # YouTube Data API v3 video statistics
        import httpx
        token = decrypt_token(account.access_token)
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params={"part": "statistics", "id": post_id, "access_token": token},
            )
            resp.raise_for_status()
            items = resp.json().get("items", [])
            if not items:
                return {}
            stats = items[0].get("statistics", {})
            return {
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "views": int(stats.get("viewCount", 0)),
                "reach": int(stats.get("viewCount", 0)),
            }

    async def get_account_insights(self, account: SocialAccount, period: str = "day") -> dict:
        return {}
