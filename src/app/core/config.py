"""
Application configuration using Pydantic Settings.
"""

import asyncio
import logging
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from watchfiles import awatch


# Determine project root (4 levels up from this file)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_NAME: str = "FastAPI Clean Architecture"
    DEBUG: bool = True
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi_clean_arch"
    API_V1_PREFIX: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


class SettingsReloader:
    """Watches .env file for changes and reloads settings."""

    def __init__(self, env_file: Path = ENV_FILE):
        self.env_file = env_file
        self.logger = logging.getLogger(__name__)
        self._running = False
        self._task = None

    async def start(self):
        """Start watching for .env changes."""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._watch_loop())
        self.logger.info(f"Started watching {self.env_file}")

    async def stop(self):
        """Stop watching for .env changes."""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self.logger.info("Stopped watching .env file")

    async def _watch_loop(self):
        """Async loop to watch for file changes."""
        try:
            async for changes in awatch(self.env_file.parent):
                if self.env_file in {Path(c[1]) for c in changes}:
                    self.logger.info("Detected .env file change, reloading settings...")
                    get_settings.cache_clear()
                    self.logger.info("Settings reloaded successfully")
        except asyncio.CancelledError:
            raise
        except Exception as e:
            self.logger.error(f"Error watching .env file: {e}")


# Create global reloader instance
reloader = SettingsReloader()
