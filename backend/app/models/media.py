"""Загруженные файлы (сами байты лежат в MinIO)."""

import uuid

from sqlalchemy import BigInteger, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, CreatedAtMixin
from app.models.enums import MediaKind, db_enum


class Media(CreatedAtMixin, Base):
    """Метаданные файла: ключ объекта, тип, размеры, длительность."""

    __tablename__ = "media"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # NULL — файл загружен админом через бота (картинки подарков/NFT)
    owner_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    kind: Mapped[MediaKind] = mapped_column(db_enum(MediaKind), nullable=False)
    object_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    thumb_key: Mapped[str | None] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    file_name: Mapped[str | None] = mapped_column(String(255))
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
