"""Проверка живости сервера и его зависимостей."""

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.redis import redis_client
from app.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)) -> ORJSONResponse:
    """Возвращает 200, если PostgreSQL и Redis доступны, иначе 503."""
    checks: dict[str, bool] = {}
    try:
        await db.execute(text("SELECT 1"))
        checks["postgres"] = True
    except Exception:  # noqa: BLE001 — любая ошибка означает недоступность
        checks["postgres"] = False
    try:
        checks["redis"] = bool(await redis_client.ping())
    except Exception:  # noqa: BLE001
        checks["redis"] = False

    ok = all(checks.values())
    return ORJSONResponse(
        status_code=200 if ok else 503,
        content={"status": "ok" if ok else "degraded", "app": settings.app_name, "checks": checks},
    )
