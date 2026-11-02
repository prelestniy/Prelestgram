"""Контакты пользователя."""

from sqlalchemy import BigInteger, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, CreatedAtMixin


class Contact(CreatedAtMixin, Base):
    """Запись в контактах owner_id о пользователе contact_user_id с локальным именем."""

    __tablename__ = "contacts"
    __table_args__ = (UniqueConstraint("owner_id", "contact_user_id", name="uq_contacts_owner_contact"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    contact_user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(64))
