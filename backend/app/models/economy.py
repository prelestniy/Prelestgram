"""Звёзды и премиум. Эмиссия — только админом через бота."""

from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, CreatedAtMixin
from app.models.enums import StarTxKind, db_enum


class StarTransaction(CreatedAtMixin, Base):
    """Запись журнала звёзд. amount > 0 — приход, amount < 0 — расход."""

    __tablename__ = "star_transactions"
    __table_args__ = (CheckConstraint("amount <> 0", name="amount_not_zero"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[StarTxKind] = mapped_column(db_enum(StarTxKind), nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # Баланс после операции — удобно показывать в истории кошелька
    balance_after: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # Вторая сторона перевода/покупки
    counterparty_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL")
    )
    admin_tg_id: Mapped[int | None] = mapped_column(BigInteger)
    user_gift_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("user_gifts.id", ondelete="SET NULL")
    )
    comment: Mapped[str | None] = mapped_column(String(255))


class PremiumGrant(CreatedAtMixin, Base):
    """История выдачи премиума админом."""

    __tablename__ = "premium_grants"
    __table_args__ = (CheckConstraint("days > 0", name="days_positive"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    days: Mapped[int] = mapped_column(Integer, nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    granted_by_tg: Mapped[int] = mapped_column(BigInteger, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    comment: Mapped[str | None] = mapped_column(Text)
