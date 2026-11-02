"""Импорт всех моделей — нужен, чтобы Alembic видел полную схему."""

from app.db.base import Base
from app.models.admin import AdminAuditLog
from app.models.auth import AuthSession, BotUser, IssuedNumber
from app.models.chat import Chat, ChatMember, Message, MessageHidden
from app.models.contact import Contact
from app.models.economy import PremiumGrant, StarTransaction
from app.models.gift import Gift, UserGift
from app.models.media import Media
from app.models.nft import NftCollection, NftItem, NftTransfer
from app.models.user import User, UserBlock, UserSettings

__all__ = [
    "AdminAuditLog",
    "AuthSession",
    "Base",
    "BotUser",
    "Chat",
    "ChatMember",
    "Contact",
    "Gift",
    "IssuedNumber",
    "Media",
    "Message",
    "MessageHidden",
    "NftCollection",
    "NftItem",
    "NftTransfer",
    "PremiumGrant",
    "StarTransaction",
    "User",
    "UserBlock",
    "UserGift",
    "UserSettings",
]
