from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Learning Assistant"
    environment: str = "local"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_learning_assistant"
    )
    redis_url: str = "redis://localhost:6379/0"
    google_api_key: str = Field(default="", repr=False)
    gemini_model: str = "gemini-2.5-flash"
    embedding_model: str = "text-embedding-004"
    embedding_dimensions: int = 768
    llm_max_retries: int = 3
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
