"""Каталог подарков и подарки, принадлежащие пользователям."""

from sqlalchemy import BigInteger, Boolean, CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, CreatedAtMixin


class Gift(CreatedAtMixin, Base):
    """Позиция каталога подарков (создаёт админ)."""

    __tablename__ = "gifts"
    __table_args__ = (
        CheckConstraint("star_price >= 0", name="star_price_non_negative"),
        CheckConstraint("total_supply IS NULL OR issued_count <= total_supply", name="supply_limit"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    # Эмодзи — запасной вариант отображения, если картинки нет
    emoji: Mapped[str] = mapped_column(String(16), nullable=False, server_default="🎁")
    image_key: Mapped[str | None] = mapped_column(String(255))
    # Цена в звёздах (используется, только если включена покупка пользователями)
    star_price: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    # NULL — неограниченный тираж
    total_supply: Mapped[int | None] = mapped_column(Integer)
    issued_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")


class UserGift(CreatedAtMixin, Base):
    """Конкретный экземпляр подарка у пользователя."""

    __tablename__ = "user_gifts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    gift_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("gifts.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    owner_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Отправитель-пользователь (если подарок куплен в приложении)
    sender_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL")
    )
    # Админ, выдавший подарок через бота
    issued_by_tg: Mapped[int | None] = mapped_column(BigInteger)
    # Порядковый номер экземпляра для лимитированных подарков (1 из N)
    serial_number: Mapped[int | None] = mapped_column(Integer)
    text: Mapped[str | None] = mapped_column(String(255))
    is_anonymous: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    # Показывать в профиле
    is_displayed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    star_price_paid: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
