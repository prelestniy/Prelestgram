"""Асинхронный движок SQLAlchemy и фабрика сессий."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# Для ≤10 пользователей небольшого пула более чем достаточно
engine = create_async_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=10,
    pool_pre_ping=True,
)

SessionFactory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncIterator[AsyncSession]:
    """Зависимость FastAPI: одна сессия БД на запрос."""
    async with SessionFactory() as session:
        yield session
