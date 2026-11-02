"""Единая настройка логирования для API и бота."""

import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    """Настраивает формат и уровень корневого логгера."""
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        stream=sys.stdout,
        force=True,
    )
    # Слишком болтливые библиотеки приглушаем
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)
