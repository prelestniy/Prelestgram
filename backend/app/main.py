"""Точка входа FastAPI-приложения Prelestgram."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.api import health
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.redis import close_redis
from app.db.session import engine

setup_logging()
logger = logging.getLogger("prelestgram")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Запуск и остановка: открываем и корректно закрываем внешние ресурсы."""
    logger.info("Запуск %s (окружение: %s)", settings.app_name, settings.app_env)
    yield
    await close_redis()
    await engine.dispose()
    logger.info("Сервер остановлен")


app = FastAPI(
    title=f"{settings.app_name} API",
    version="1.0.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    # Документацию API показываем только в режиме разработки
    docs_url="/docs" if settings.is_dev else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.is_dev else None,
)

# Все маршруты API живут под префиксом /api
app.include_router(health.router, prefix="/api")
