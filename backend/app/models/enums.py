"""Перечисления предметной области. Хранятся в БД как строки (VARCHAR + CHECK)."""

from enum import StrEnum

from sqlalchemy import Enum as SAEnum


def db_enum(enum_cls: type[StrEnum], name: str | None = None, length: int = 24) -> SAEnum:
    """Строковое перечисление без нативного типа PostgreSQL — проще мигрировать.

    name задаёт имя CHECK-ограничения; обязателен, если в одной таблице
    несколько колонок с одним и тем же перечислением.
    """
    return SAEnum(
        enum_cls,
        native_enum=False,
        length=length,
        values_callable=lambda items: [item.value for item in items],
        validate_strings=True,
        name=name or enum_cls.__name__.lower(),
        create_constraint=True,
    )


class ChatType(StrEnum):
    """Тип чата."""

    PRIVATE = "private"  # личная переписка (в т.ч. «Избранное» — чат с самим собой)
    GROUP = "group"  # группа


class MemberRole(StrEnum):
    """Роль участника в чате."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class MessageType(StrEnum):
    """Тип сообщения."""

    TEXT = "text"
    PHOTO = "photo"
    VIDEO = "video"
    VOICE = "voice"
    FILE = "file"
    GIFT = "gift"  # сообщение о подаренном подарке
    SERVICE = "service"  # системное: создание группы, вход участника и т.п.


class MediaKind(StrEnum):
    """Назначение загруженного файла."""

    PHOTO = "photo"
    VIDEO = "video"
    VOICE = "voice"
    FILE = "file"
    AVATAR = "avatar"
    GIFT_IMAGE = "gift_image"
    NFT_IMAGE = "nft_image"


class PrivacyLevel(StrEnum):
    """Кто видит данные пользователя."""

    EVERYBODY = "everybody"
    CONTACTS = "contacts"
    NOBODY = "nobody"


class ThemeMode(StrEnum):
    """Тема оформления клиента."""

    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"


class StarTxKind(StrEnum):
    """Вид операции со звёздами."""

    ADMIN_GRANT = "admin_grant"  # начисление админом
    ADMIN_REVOKE = "admin_revoke"  # списание админом
    TRANSFER_IN = "transfer_in"  # входящий перевод от пользователя
    TRANSFER_OUT = "transfer_out"  # исходящий перевод пользователю
    GIFT_PURCHASE = "gift_purchase"  # покупка подарка для другого пользователя


class NftTransferKind(StrEnum):
    """Вид движения NFT во внутреннем реестре."""

    MINT = "mint"  # выпуск админом
    ADMIN_TRANSFER = "admin_transfer"  # передача админом
    USER_TRANSFER = "user_transfer"  # передача между пользователями
    BURN = "burn"  # изъятие админом
