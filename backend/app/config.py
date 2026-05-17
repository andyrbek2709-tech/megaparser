from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_ENV: str = "development"
    SECRET_KEY: str = "changeme"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/social_engine"
    SYNC_DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/social_engine"

    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    def model_post_init(self, __context) -> None:
        # Railway provides plain postgresql:// — patch to asyncpg variant
        for prefix, replacement in [("postgres://", "postgresql+asyncpg://"), ("postgresql://", "postgresql+asyncpg://")]:
            if self.DATABASE_URL.startswith(prefix):
                object.__setattr__(self, "DATABASE_URL", self.DATABASE_URL.replace(prefix, "postgresql+asyncpg://", 1))
        if self.SYNC_DATABASE_URL.startswith("postgres://"):
            object.__setattr__(self, "SYNC_DATABASE_URL", self.SYNC_DATABASE_URL.replace("postgres://", "postgresql://", 1))

    OPENAI_API_KEY: str = ""
    OPENAI_TEXT_MODEL: str = "gpt-4o-mini"
    OPENAI_IMAGE_MODEL: str = "dall-e-3"
    OPENAI_IMAGE_SIZE: str = "1024x1024"

    INSTAGRAM_APP_ID: str = ""
    INSTAGRAM_APP_SECRET: str = ""
    INSTAGRAM_REDIRECT_URI: str = "http://localhost:8000/api/v1/accounts/instagram/callback"

    YOUTUBE_API_KEY: str = ""
    YOUTUBE_CLIENT_ID: str = ""
    YOUTUBE_CLIENT_SECRET: str = ""

    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    REDDIT_USER_AGENT: str = "social-engine:v1.0"

    MEDIA_STORAGE_PATH: str = "./media"
    ML_MODELS_PATH: str = "./ml_models"
    ENGAGEMENT_MODEL_MIN_SAMPLES: int = 50

    FERNET_KEY: str = ""

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


settings = Settings()
