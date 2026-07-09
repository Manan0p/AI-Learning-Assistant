from __future__ import annotations

import sys

from loguru import logger

from app.core.config import settings


def configure_logging() -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.log_level,
        serialize=settings.environment != "local",
        backtrace=settings.debug,
        diagnose=settings.debug,
    )
