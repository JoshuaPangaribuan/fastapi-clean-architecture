"""
Logging configuration for the application.

This module sets up structured logging with appropriate formatters and handlers
for both development and production environments.
"""

import logging
import sys
from pathlib import Path

from app.core.config import get_settings


def setup_logging() -> None:
    """Configure application logging.

    Sets up console logging for development and optional file logging for
    production. Suppresses noisy third-party logs.
    """
    settings = get_settings()

    # Define log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    detailed_format = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "[%(error_code)s] %(message)s - Path: %(path)s - Method: %(method)s"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    root_logger.addHandler(console_handler)

    # Optional file handler for production
    if not settings.DEBUG:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "app.log")
        file_handler.setFormatter(logging.Formatter(detailed_format))
        root_logger.addHandler(file_handler)

    # Suppress noisy third-party logs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
