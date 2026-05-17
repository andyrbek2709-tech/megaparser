from abc import ABC, abstractmethod
from app.models.social_account import SocialAccount


class BasePlatform(ABC):
    @abstractmethod
    async def publish_photo(self, account: SocialAccount, image_url: str, caption: str) -> str:
        pass

    @abstractmethod
    async def get_post_insights(self, account: SocialAccount, post_id: str) -> dict:
        pass

    @abstractmethod
    async def get_account_insights(self, account: SocialAccount, period: str) -> dict:
        pass
