"""
Application configuration using Pydantic Settings.
"""

from functools import lru_cache


class Settings:
    """Application settings loaded from environment variables."""

    APP_NAME: str = "FastAPI Clean Architecture"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/fastapi-clean-arch.db"

    # API
    API_V1_PREFIX: str = "/api/v1"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
