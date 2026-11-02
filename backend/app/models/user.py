"""Пользователь, его настройки и чёрный список."""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin, TimestampMixin
from app.models.enums import PrivacyLevel, ThemeMode, db_enum


class User(TimestampMixin, Base):
    """Аккаунт Prelestgram. Создаётся после подтверждения кода из Telegram-бота."""

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("stars_balance >= 0", name="stars_balance_non_negative"),
        # Юзернейм уникален без учёта регистра
        Index("uq_users_username_lower", func.lower(text("username")), unique=True),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    phone: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    # Telegram ID владельца номера — туда бот присылает коды входа
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)

    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(64))
    username: Mapped[str | None] = mapped_column(String(32))
    bio: Mapped[str | None] = mapped_column(String(140))
    # Ключ объекта аватарки в MinIO
    avatar_key: Mapped[str | None] = mapped_column(String(255))
    # Эмодзи-статус (доступен с премиумом)
    emoji_status: Mapped[str | None] = mapped_column(String(16))

    # Премиум активен, пока premium_until в будущем
    premium_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    stars_balance: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default="0")
    # Адрес внутреннего кошелька (для NFT и звёзд), вида PG + 32 символа
    wallet_address: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)

    is_banned: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    settings: Mapped["UserSettings"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="selectin"
    )


class UserSettings(Base):
    """Настройки клиента и приватности. Синхронизируются между устройствами."""

    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    theme: Mapped[ThemeMode] = mapped_column(
        db_enum(ThemeMode), nullable=False, server_default=ThemeMode.SYSTEM.value
    )
    language: Mapped[str] = mapped_column(String(8), nullable=False, server_default="ru")
    chat_text_size: Mapped[int] = mapped_column(Integer, nullable=False, server_default="16")
    send_by_enter: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    auto_download_media: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    # Уведомления
    notify_private: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    notify_groups: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    show_previews: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    in_app_sounds: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    # Приватность
    privacy_last_seen: Mapped[PrivacyLevel] = mapped_column(
        db_enum(PrivacyLevel, name="privacy_last_seen"), nullable=False, server_default=PrivacyLevel.EVERYBODY.value
    )
    privacy_phone: Mapped[PrivacyLevel] = mapped_column(
        db_enum(PrivacyLevel, name="privacy_phone"), nullable=False, server_default=PrivacyLevel.CONTACTS.value
    )
    privacy_avatar: Mapped[PrivacyLevel] = mapped_column(
        db_enum(PrivacyLevel, name="privacy_avatar"), nullable=False, server_default=PrivacyLevel.EVERYBODY.value
    )
    privacy_gifts: Mapped[PrivacyLevel] = mapped_column(
        db_enum(PrivacyLevel, name="privacy_gifts"), nullable=False, server_default=PrivacyLevel.EVERYBODY.value
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="settings")


class UserBlock(CreatedAtMixin, Base):
    """Чёрный список: blocker_id не получает сообщения от blocked_id."""

    __tablename__ = "user_blocks"

    blocker_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    blocked_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
