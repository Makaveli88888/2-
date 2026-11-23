from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    xai_api_key: str = ""
    xai_model: str = "grok-4-fast"
    ai_provider: str = "hybrid"
    jwt_secret: str = ""
    database_url: str = "postgresql+psycopg://joker:joker@postgres:5432/joker"
    redis_url: str = "redis://redis:6379/0"
    telegram_bot_token: str = ""
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    max_tool_rounds: int = 4

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
