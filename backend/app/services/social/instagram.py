import asyncio
from datetime import datetime, timedelta, timezone

import httpx
import structlog

from app.config import settings
from app.models.social_account import SocialAccount
from app.services.social.base_platform import BasePlatform

logger = structlog.get_logger()

INSTAGRAM_BASE = "https://graph.instagram.com/v21.0"
RATE_LIMIT_CALLS = 200
RATE_LIMIT_WINDOW = 3600


class InstagramClient(BasePlatform):
    def __init__(self) -> None:
        self._call_count = 0
        self._window_start = datetime.now(timezone.utc)

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        await self._check_rate_limit()
        url = f"{INSTAGRAM_BASE}{path}"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()

    async def _check_rate_limit(self) -> None:
        now = datetime.now(timezone.utc)
        if (now - self._window_start).total_seconds() > RATE_LIMIT_WINDOW:
            self._call_count = 0
            self._window_start = now
        if self._call_count >= RATE_LIMIT_CALLS - 10:
            wait = RATE_LIMIT_WINDOW - (now - self._window_start).total_seconds()
            if wait > 0:
                logger.warning("instagram_rate_limit_approaching", wait_seconds=wait)
                await asyncio.sleep(min(wait, 60))
        self._call_count += 1

    def _get_token(self, account: SocialAccount) -> str:
        from app.services.security import decrypt_token
        return decrypt_token(account.access_token)

    async def publish_photo(self, account: SocialAccount, image_url: str, caption: str) -> str:
        token = self._get_token(account)
        container = await self._request(
            "POST",
            f"/{account.platform_user_id}/media",
            params={"image_url": image_url, "caption": caption[:2200], "access_token": token},
        )
        container_id = container["id"]
        await asyncio.sleep(5)
        result = await self._request(
            "POST",
            f"/{account.platform_user_id}/media_publish",
            params={"creation_id": container_id, "access_token": token},
        )
        return result["id"]

    async def publish_reel(self, account: SocialAccount, video_url: str, caption: str) -> str:
        token = self._get_token(account)
        container = await self._request(
            "POST",
            f"/{account.platform_user_id}/media",
            params={"media_type": "REELS", "video_url": video_url, "caption": caption[:2200], "access_token": token},
        )
        container_id = container["id"]
        for _ in range(12):
            await asyncio.sleep(10)
            status = await self._request("GET", f"/{container_id}", params={"fields": "status_code", "access_token": token})
            if status.get("status_code") == "FINISHED":
                break
        result = await self._request(
            "POST",
            f"/{account.platform_user_id}/media_publish",
            params={"creation_id": container_id, "access_token": token},
        )
        return result["id"]

    async def get_post_insights(self, account: SocialAccount, post_id: str) -> dict:
        token = self._get_token(account)
        result = await self._request(
            "GET",
            f"/{post_id}/insights",
            params={"metric": "impressions,reach,likes,comments,shares,saved", "access_token": token},
        )
        metrics: dict = {}
        for item in result.get("data", []):
            metrics[item["name"]] = item["values"][0]["value"] if item.get("values") else 0
        return metrics

    async def get_account_insights(self, account: SocialAccount, period: str = "day") -> dict:
        token = self._get_token(account)
        return await self._request(
            "GET",
            f"/{account.platform_user_id}/insights",
            params={"metric": "impressions,reach,profile_views", "period": period, "access_token": token},
        )

    async def refresh_token(self, account: SocialAccount) -> SocialAccount:
        token = self._get_token(account)
        result = await self._request(
            "GET",
            "/refresh_access_token",
            params={"grant_type": "ig_refresh_token", "access_token": token},
        )
        from app.services.security import encrypt_token
        account.access_token = encrypt_token(result["access_token"])
        account.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=result.get("expires_in", 5184000))
        return account

    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.instagram.com/oauth/access_token",
                data={
                    "client_id": settings.INSTAGRAM_APP_ID,
                    "client_secret": settings.INSTAGRAM_APP_SECRET,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                    "code": code,
                },
            )
            response.raise_for_status()
            short_token = response.json()

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://graph.instagram.com/access_token",
                params={
                    "grant_type": "ig_exchange_token",
                    "client_secret": settings.INSTAGRAM_APP_SECRET,
                    "access_token": short_token["access_token"],
                },
            )
            response.raise_for_status()
            long_token = response.json()

        profile = await self._request(
            "GET",
            f"/{short_token['user_id']}",
            params={"fields": "id,username,account_type", "access_token": long_token["access_token"]},
        )
        return {
            "access_token": long_token["access_token"],
            "user_id": str(short_token["user_id"]),
            "username": profile.get("username"),
            "account_type": profile.get("account_type", "business"),
            "expires_at": datetime.now(timezone.utc) + timedelta(days=60),
        }
