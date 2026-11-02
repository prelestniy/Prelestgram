"""Внутренний реестр NFT (без блокчейна)."""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, CreatedAtMixin
from app.models.enums import NftTransferKind, db_enum


class NftCollection(CreatedAtMixin, Base):
    """Коллекция коллекционных предметов."""

    __tablename__ = "nft_collections"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    emoji: Mapped[str] = mapped_column(String(16), nullable=False, server_default="💎")
    image_key: Mapped[str | None] = mapped_column(String(255))


class NftItem(Base):
    """Единица NFT. Номер уникален внутри коллекции."""

    __tablename__ = "nft_items"
    __table_args__ = (
        UniqueConstraint("collection_id", "serial", name="uq_nft_items_collection_serial"),
        CheckConstraint("rarity_permille BETWEEN 1 AND 1000", name="rarity_range"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    collection_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("nft_collections.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    serial: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    # Атрибуты в стиле коллекционных подарков Telegram
    model: Mapped[str | None] = mapped_column(String(64))
    backdrop: Mapped[str | None] = mapped_column(String(64))
    # Цвет фона карточки в формате #RRGGBB
    backdrop_color: Mapped[str | None] = mapped_column(String(7))
    symbol: Mapped[str | None] = mapped_column(String(64))
    # Редкость в промилле: 1 = 0.1%, 1000 = 100%
    rarity_permille: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1000")
    image_key: Mapped[str | None] = mapped_column(String(255))
    # NULL — предмет изъят (сожжён)
    owner_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    is_displayed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    minted_by_tg: Mapped[int] = mapped_column(BigInteger, nullable=False)
    minted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class NftTransfer(CreatedAtMixin, Base):
    """Журнал движения NFT — аналог истории транзакций в блокчейне."""

    __tablename__ = "nft_transfers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nft_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("nft_items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[NftTransferKind] = mapped_column(db_enum(NftTransferKind), nullable=False)
    from_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL")
    )
    to_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL")
    )
    admin_tg_id: Mapped[int | None] = mapped_column(BigInteger)
    comment: Mapped[str | None] = mapped_column(String(255))
