import structlog
import praw

from app.config import settings
from app.models.social_account import SocialAccount
from app.services.social.base_platform import BasePlatform

logger = structlog.get_logger()


class RedditClient(BasePlatform):
    def _get_reddit(self, account: SocialAccount) -> praw.Reddit:
        from app.services.security import decrypt_token
        return praw.Reddit(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET,
            user_agent=settings.REDDIT_USER_AGENT,
            refresh_token=decrypt_token(account.access_token),
        )

    async def publish_photo(self, account: SocialAccount, image_url: str, caption: str) -> str:
        reddit = self._get_reddit(account)
        meta = account.metadata_ or {}
        subreddit = meta.get("subreddit", "test")
        submission = reddit.subreddit(subreddit).submit(title=caption[:300], url=image_url)
        return submission.id

    async def get_post_insights(self, account: SocialAccount, post_id: str) -> dict:
        reddit = self._get_reddit(account)
        submission = reddit.submission(id=post_id)
        return {"likes": submission.score, "comments": submission.num_comments, "reach": submission.score, "shares": 0, "saves": submission.saved}

    async def get_account_insights(self, account: SocialAccount, period: str = "day") -> dict:
        return {}
