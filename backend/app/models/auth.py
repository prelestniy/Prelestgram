"""Связка с Telegram-ботом, выданные номера и сессии устройств."""

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, CreatedAtMixin, TimestampMixin


class BotUser(TimestampMixin, Base):
    """Пользователь настоящего Telegram, нажавший /start в боте.

    Без этой записи бот не может написать человеку, поэтому номер выдаётся
    только тем, кто уже запустил бота.
    """

    __tablename__ = "bot_users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[str | None] = mapped_column(String(64), index=True)
    first_name: Mapped[str | None] = mapped_column(String(128))
    last_name: Mapped[str | None] = mapped_column(String(128))
    language_code: Mapped[str | None] = mapped_column(String(8))
    # True, если человек заблокировал бота — коды доставить невозможно
    is_bot_blocked: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")


class IssuedNumber(CreatedAtMixin, Base):
    """Кастомный номер, выданный админом конкретному Telegram-пользователю."""

    __tablename__ = "issued_numbers"

    phone: Mapped[str] = mapped_column(String(16), primary_key=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("bot_users.telegram_id", ondelete="CASCADE"), nullable=False, index=True
    )
    issued_by_tg: Mapped[int] = mapped_column(BigInteger, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    is_revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    # Заполняется после первой успешной регистрации по номеру
    user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), unique=True
    )


class AuthSession(CreatedAtMixin, Base):
    """Сессия устройства. Хранит только хэш refresh-токена."""

    __tablename__ = "auth_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    refresh_token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    device_model: Mapped[str | None] = mapped_column(String(128))
    platform: Mapped[str | None] = mapped_column(String(32))
    app_version: Mapped[str | None] = mapped_column(String(32))
    ip_address: Mapped[str | None] = mapped_column(String(64))
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
