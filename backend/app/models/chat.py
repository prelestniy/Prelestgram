"""Чаты, участники и сообщения."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, CreatedAtMixin
from app.models.enums import ChatType, MemberRole, MessageType, db_enum


class Chat(CreatedAtMixin, Base):
    """Личный чат или группа."""

    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    type: Mapped[ChatType] = mapped_column(db_enum(ChatType), nullable=False)
    # Для личных чатов: "<меньший id>:<больший id>" — гарантирует один чат на пару
    pair_key: Mapped[str | None] = mapped_column(String(48), unique=True)
    title: Mapped[str | None] = mapped_column(String(128))
    description: Mapped[str | None] = mapped_column(String(255))
    avatar_key: Mapped[str | None] = mapped_column(String(255))
    created_by_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL")
    )
    # Денормализация для быстрой сортировки списка чатов
    last_message_id: Mapped[int | None] = mapped_column(BigInteger)
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class ChatMember(Base):
    """Участник чата и его персональное состояние чата."""

    __tablename__ = "chat_members"

    chat_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("chats.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    role: Mapped[MemberRole] = mapped_column(
        db_enum(MemberRole), nullable=False, server_default=MemberRole.MEMBER.value
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    # Последнее прочитанное этим участником сообщение
    last_read_message_id: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default="0")
    # «Очистить историю» только для себя: всё с id <= этого значения скрыто
    cleared_before_message_id: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default="0")
    is_pinned: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    pinned_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    muted_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # Участник вышел из группы (история остаётся, новые сообщения не приходят)
    has_left: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")


class Message(CreatedAtMixin, Base):
    """Сообщение в чате."""

    __tablename__ = "messages"
    __table_args__ = (Index("ix_messages_chat_id_id", "chat_id", "id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False
    )
    # NULL — системное сообщение
    sender_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    type: Mapped[MessageType] = mapped_column(db_enum(MessageType), nullable=False)
    text: Mapped[str | None] = mapped_column(Text)
    media_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("media.id", ondelete="SET NULL")
    )
    reply_to_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("messages.id", ondelete="SET NULL")
    )
    # Пересланное сообщение: автор оригинала
    forward_from_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL")
    )
    # Для сообщений-подарков: ссылка на экземпляр подарка
    user_gift_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("user_gifts.id", ondelete="SET NULL")
    )
    # Данные системного сообщения: {"action": "group_created", ...}
    service_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    # Клиентский идентификатор для защиты от дублей при переотправке
    client_random_id: Mapped[str | None] = mapped_column(String(64))
    edited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # «Удалить у всех» — мягкое удаление
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class MessageHidden(Base):
    """«Удалить только у меня» — сообщение скрыто для конкретного пользователя."""

    __tablename__ = "message_hidden"

    message_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("messages.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
