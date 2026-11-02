"""Общий асинхронный клиент Redis."""

from redis.asyncio import Redis

from app.core.config import settings

# Один пул соединений на процесс; decode_responses — работаем со строками
redis_client: Redis = Redis.from_url(settings.redis_url, decode_responses=True)


async def close_redis() -> None:
    """Корректно закрывает пул соединений при остановке приложения."""
    await redis_client.aclose()
