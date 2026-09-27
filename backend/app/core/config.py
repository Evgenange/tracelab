from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TraceLab"
    environment: str = "development"

    database_url: str = "postgresql+psycopg://tracelab:tracelab@localhost:5433/tracelab"
    redis_url: str = "redis://localhost:6379/0"

    storage_path: str = "storage"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
