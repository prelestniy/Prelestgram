"""Начальная схема Prelestgram: пользователи, авторизация, чаты, медиа, звёзды, подарки, NFT.

Ревизия: 0001_initial
Предыдущая: нет
Создана: 2026-11-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Создание всех таблиц и индексов."""
    op.create_table('admin_audit_log',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('admin_tg_id', sa.BigInteger(), nullable=False),
    sa.Column('action', sa.String(length=64), nullable=False),
    sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_admin_audit_log'))
    )
    op.create_index(op.f('ix_admin_audit_log_admin_tg_id'), 'admin_audit_log', ['admin_tg_id'], unique=False)
    op.create_table('bot_users',
    sa.Column('telegram_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('first_name', sa.String(length=128), nullable=True),
    sa.Column('last_name', sa.String(length=128), nullable=True),
    sa.Column('language_code', sa.String(length=8), nullable=True),
    sa.Column('is_bot_blocked', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('telegram_id', name=op.f('pk_bot_users'))
    )
    op.create_index(op.f('ix_bot_users_username'), 'bot_users', ['username'], unique=False)
    op.create_table('gifts',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('slug', sa.String(length=64), nullable=False),
    sa.Column('title', sa.String(length=64), nullable=False),
    sa.Column('emoji', sa.String(length=16), server_default='🎁', nullable=False),
    sa.Column('image_key', sa.String(length=255), nullable=True),
    sa.Column('star_price', sa.Integer(), server_default='0', nullable=False),
    sa.Column('total_supply', sa.Integer(), nullable=True),
    sa.Column('issued_count', sa.Integer(), server_default='0', nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('star_price >= 0', name=op.f('ck_gifts_star_price_non_negative')),
    sa.CheckConstraint('total_supply IS NULL OR issued_count <= total_supply', name=op.f('ck_gifts_supply_limit')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_gifts')),
    sa.UniqueConstraint('slug', name=op.f('uq_gifts_slug'))
    )
    op.create_table('nft_collections',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('slug', sa.String(length=64), nullable=False),
    sa.Column('title', sa.String(length=64), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('emoji', sa.String(length=16), server_default='💎', nullable=False),
    sa.Column('image_key', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_nft_collections')),
    sa.UniqueConstraint('slug', name=op.f('uq_nft_collections_slug'))
    )
    op.create_table('users',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('phone', sa.String(length=16), nullable=False),
    sa.Column('telegram_id', sa.BigInteger(), nullable=False),
    sa.Column('first_name', sa.String(length=64), nullable=False),
    sa.Column('last_name', sa.String(length=64), nullable=True),
    sa.Column('username', sa.String(length=32), nullable=True),
    sa.Column('bio', sa.String(length=140), nullable=True),
    sa.Column('avatar_key', sa.String(length=255), nullable=True),
    sa.Column('emoji_status', sa.String(length=16), nullable=True),
    sa.Column('premium_until', sa.DateTime(timezone=True), nullable=True),
    sa.Column('stars_balance', sa.BigInteger(), server_default='0', nullable=False),
    sa.Column('wallet_address', sa.String(length=40), nullable=False),
    sa.Column('is_banned', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('stars_balance >= 0', name=op.f('ck_users_stars_balance_non_negative')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('phone', name=op.f('uq_users_phone')),
    sa.UniqueConstraint('wallet_address', name=op.f('uq_users_wallet_address'))
    )
    op.create_index(op.f('ix_users_telegram_id'), 'users', ['telegram_id'], unique=False)
    op.create_index('uq_users_username_lower', 'users', [sa.text('lower(username)')], unique=True)
    op.create_table('auth_sessions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('refresh_token_hash', sa.String(length=64), nullable=False),
    sa.Column('device_model', sa.String(length=128), nullable=True),
    sa.Column('platform', sa.String(length=32), nullable=True),
    sa.Column('app_version', sa.String(length=32), nullable=True),
    sa.Column('ip_address', sa.String(length=64), nullable=True),
    sa.Column('last_active_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_auth_sessions_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_auth_sessions')),
    sa.UniqueConstraint('refresh_token_hash', name=op.f('uq_auth_sessions_refresh_token_hash'))
    )
    op.create_index(op.f('ix_auth_sessions_user_id'), 'auth_sessions', ['user_id'], unique=False)
    op.create_table('chats',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('type', sa.Enum('private', 'group', name='chattype', native_enum=False, create_constraint=True, length=24), nullable=False),
    sa.Column('pair_key', sa.String(length=48), nullable=True),
    sa.Column('title', sa.String(length=128), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('avatar_key', sa.String(length=255), nullable=True),
    sa.Column('created_by_id', sa.BigInteger(), nullable=True),
    sa.Column('last_message_id', sa.BigInteger(), nullable=True),
    sa.Column('last_message_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name=op.f('fk_chats_created_by_id_users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_chats')),
    sa.UniqueConstraint('pair_key', name=op.f('uq_chats_pair_key'))
    )
    op.create_index(op.f('ix_chats_last_message_at'), 'chats', ['last_message_at'], unique=False)
    op.create_table('contacts',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('owner_id', sa.BigInteger(), nullable=False),
    sa.Column('contact_user_id', sa.BigInteger(), nullable=False),
    sa.Column('first_name', sa.String(length=64), nullable=False),
    sa.Column('last_name', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['contact_user_id'], ['users.id'], name=op.f('fk_contacts_contact_user_id_users'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name=op.f('fk_contacts_owner_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_contacts')),
    sa.UniqueConstraint('owner_id', 'contact_user_id', name='uq_contacts_owner_contact')
    )
    op.create_index(op.f('ix_contacts_contact_user_id'), 'contacts', ['contact_user_id'], unique=False)
    op.create_index(op.f('ix_contacts_owner_id'), 'contacts', ['owner_id'], unique=False)
    op.create_table('issued_numbers',
    sa.Column('phone', sa.String(length=16), nullable=False),
    sa.Column('telegram_id', sa.BigInteger(), nullable=False),
    sa.Column('issued_by_tg', sa.BigInteger(), nullable=False),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('is_revoked', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['telegram_id'], ['bot_users.telegram_id'], name=op.f('fk_issued_numbers_telegram_id_bot_users'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_issued_numbers_user_id_users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('phone', name=op.f('pk_issued_numbers')),
    sa.UniqueConstraint('user_id', name=op.f('uq_issued_numbers_user_id'))
    )
    op.create_index(op.f('ix_issued_numbers_telegram_id'), 'issued_numbers', ['telegram_id'], unique=False)
    op.create_table('media',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('owner_id', sa.BigInteger(), nullable=True),
    sa.Column('kind', sa.Enum('photo', 'video', 'voice', 'file', 'avatar', 'gift_image', 'nft_image', name='mediakind', native_enum=False, create_constraint=True, length=24), nullable=False),
    sa.Column('object_key', sa.String(length=255), nullable=False),
    sa.Column('thumb_key', sa.String(length=255), nullable=True),
    sa.Column('mime_type', sa.String(length=128), nullable=False),
    sa.Column('size_bytes', sa.BigInteger(), nullable=False),
    sa.Column('file_name', sa.String(length=255), nullable=True),
    sa.Column('width', sa.Integer(), nullable=True),
    sa.Column('height', sa.Integer(), nullable=True),
    sa.Column('duration_ms', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name=op.f('fk_media_owner_id_users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_media')),
    sa.UniqueConstraint('object_key', name=op.f('uq_media_object_key'))
    )
    op.create_index(op.f('ix_media_owner_id'), 'media', ['owner_id'], unique=False)
    op.create_table('nft_items',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('collection_id', sa.BigInteger(), nullable=False),
    sa.Column('serial', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=64), nullable=False),
    sa.Column('model', sa.String(length=64), nullable=True),
    sa.Column('backdrop', sa.String(length=64), nullable=True),
    sa.Column('backdrop_color', sa.String(length=7), nullable=True),
    sa.Column('symbol', sa.String(length=64), nullable=True),
    sa.Column('rarity_permille', sa.Integer(), server_default='1000', nullable=False),
    sa.Column('image_key', sa.String(length=255), nullable=True),
    sa.Column('owner_id', sa.BigInteger(), nullable=True),
    sa.Column('is_displayed', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('minted_by_tg', sa.BigInteger(), nullable=False),
    sa.Column('minted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('rarity_permille BETWEEN 1 AND 1000', name=op.f('ck_nft_items_rarity_range')),
    sa.ForeignKeyConstraint(['collection_id'], ['nft_collections.id'], name=op.f('fk_nft_items_collection_id_nft_collections'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name=op.f('fk_nft_items_owner_id_users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_nft_items')),
    sa.UniqueConstraint('collection_id', 'serial', name='uq_nft_items_collection_serial')
    )
    op.create_index(op.f('ix_nft_items_collection_id'), 'nft_items', ['collection_id'], unique=False)
    op.create_index(op.f('ix_nft_items_owner_id'), 'nft_items', ['owner_id'], unique=False)
    op.create_table('premium_grants',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('days', sa.Integer(), nullable=False),
    sa.Column('starts_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('ends_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('granted_by_tg', sa.BigInteger(), nullable=False),
    sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('days > 0', name=op.f('ck_premium_grants_days_positive')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_premium_grants_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_premium_grants'))
    )
    op.create_index(op.f('ix_premium_grants_user_id'), 'premium_grants', ['user_id'], unique=False)
    op.create_table('user_blocks',
    sa.Column('blocker_id', sa.BigInteger(), nullable=False),
    sa.Column('blocked_id', sa.BigInteger(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['blocked_id'], ['users.id'], name=op.f('fk_user_blocks_blocked_id_users'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['blocker_id'], ['users.id'], name=op.f('fk_user_blocks_blocker_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('blocker_id', 'blocked_id', name=op.f('pk_user_blocks'))
    )
    op.create_table('user_gifts',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('gift_id', sa.BigInteger(), nullable=False),
    sa.Column('owner_id', sa.BigInteger(), nullable=False),
    sa.Column('sender_user_id', sa.BigInteger(), nullable=True),
    sa.Column('issued_by_tg', sa.BigInteger(), nullable=True),
    sa.Column('serial_number', sa.Integer(), nullable=True),
    sa.Column('text', sa.String(length=255), nullable=True),
    sa.Column('is_anonymous', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('is_displayed', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('star_price_paid', sa.Integer(), server_default='0', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['gift_id'], ['gifts.id'], name=op.f('fk_user_gifts_gift_id_gifts'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name=op.f('fk_user_gifts_owner_id_users'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['sender_user_id'], ['users.id'], name=op.f('fk_user_gifts_sender_user_id_users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user_gifts'))
    )
    op.create_index(op.f('ix_user_gifts_gift_id'), 'user_gifts', ['gift_id'], unique=False)
    op.create_index(op.f('ix_user_gifts_owner_id'), 'user_gifts', ['owner_id'], unique=False)
    op.create_table('user_settings',
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('theme', sa.Enum('system', 'light', 'dark', name='thememode', native_enum=False, create_constraint=True, length=24), server_default='system', nullable=False),
    sa.Column('language', sa.String(length=8), server_default='ru', nullable=False),
    sa.Column('chat_text_size', sa.Integer(), server_default='16', nullable=False),
    sa.Column('send_by_enter', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('auto_download_media', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('notify_private', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('notify_groups', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('show_previews', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('in_app_sounds', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('privacy_last_seen', sa.Enum('everybody', 'contacts', 'nobody', name='privacy_last_seen', native_enum=False, create_constraint=True, length=24), server_default='everybody', nullable=False),
    sa.Column('privacy_phone', sa.Enum('everybody', 'contacts', 'nobody', name='privacy_phone', native_enum=False, create_constraint=True, length=24), server_default='contacts', nullable=False),
    sa.Column('privacy_avatar', sa.Enum('everybody', 'contacts', 'nobody', name='privacy_avatar', native_enum=False, create_constraint=True, length=24), server_default='everybody', nullable=False),
    sa.Column('privacy_gifts', sa.Enum('everybody', 'contacts', 'nobody', name='privacy_gifts', native_enum=False, create_constraint=True, length=24), server_default='everybody', nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_user_settings_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', name=op.f('pk_user_settings'))
    )
    op.create_table('chat_members',
    sa.Column('chat_id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('role', sa.Enum('owner', 'admin', 'member', name='memberrole', native_enum=False, create_constraint=True, length=24), server_default='member', nullable=False),
    sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('last_read_message_id', sa.BigInteger(), server_default='0', nullable=False),
    sa.Column('cleared_before_message_id', sa.BigInteger(), server_default='0', nullable=False),
    sa.Column('is_pinned', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('pinned_order', sa.Integer(), server_default='0', nullable=False),
    sa.Column('is_archived', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('muted_until', sa.DateTime(timezone=True), nullable=True),
    sa.Column('has_left', sa.Boolean(), server_default='false', nullable=False),
    sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], name=op.f('fk_chat_members_chat_id_chats'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_chat_members_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('chat_id', 'user_id', name=op.f('pk_chat_members'))
    )
    op.create_index(op.f('ix_chat_members_user_id'), 'chat_members', ['user_id'], unique=False)
    op.create_table('messages',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('chat_id', sa.BigInteger(), nullable=False),
    sa.Column('sender_id', sa.BigInteger(), nullable=True),
    sa.Column('type', sa.Enum('text', 'photo', 'video', 'voice', 'file', 'gift', 'service', name='messagetype', native_enum=False, create_constraint=True, length=24), nullable=False),
    sa.Column('text', sa.Text(), nullable=True),
    sa.Column('media_id', sa.UUID(), nullable=True),
    sa.Column('reply_to_id', sa.BigInteger(), nullable=True),
    sa.Column('forward_from_user_id', sa.BigInteger(), nullable=True),
    sa.Column('user_gift_id', sa.BigInteger(), nullable=True),
    sa.Column('service_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('client_random_id', sa.String(length=64), nullable=True),
    sa.Column('edited_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], name=op.f('fk_messages_chat_id_chats'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['forward_from_user_id'], ['users.id'], name=op.f('fk_messages_forward_from_user_id_users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['media_id'], ['media.id'], name=op.f('fk_messages_media_id_media'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['reply_to_id'], ['messages.id'], name=op.f('fk_messages_reply_to_id_messages'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['sender_id'], ['users.id'], name=op.f('fk_messages_sender_id_users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_gift_id'], ['user_gifts.id'], name=op.f('fk_messages_user_gift_id_user_gifts'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_messages'))
    )
    op.create_index('ix_messages_chat_id_id', 'messages', ['chat_id', 'id'], unique=False)
    op.create_index(op.f('ix_messages_sender_id'), 'messages', ['sender_id'], unique=False)
    op.create_table('nft_transfers',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('nft_id', sa.BigInteger(), nullable=False),
    sa.Column('kind', sa.Enum('mint', 'admin_transfer', 'user_transfer', 'burn', name='nfttransferkind', native_enum=False, create_constraint=True, length=24), nullable=False),
    sa.Column('from_user_id', sa.BigInteger(), nullable=True),
    sa.Column('to_user_id', sa.BigInteger(), nullable=True),
    sa.Column('admin_tg_id', sa.BigInteger(), nullable=True),
    sa.Column('comment', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['from_user_id'], ['users.id'], name=op.f('fk_nft_transfers_from_user_id_users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['nft_id'], ['nft_items.id'], name=op.f('fk_nft_transfers_nft_id_nft_items'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['to_user_id'], ['users.id'], name=op.f('fk_nft_transfers_to_user_id_users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_nft_transfers'))
    )
    op.create_index(op.f('ix_nft_transfers_nft_id'), 'nft_transfers', ['nft_id'], unique=False)
    op.create_table('star_transactions',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('kind', sa.Enum('admin_grant', 'admin_revoke', 'transfer_in', 'transfer_out', 'gift_purchase', name='startxkind', native_enum=False, create_constraint=True, length=24), nullable=False),
    sa.Column('amount', sa.BigInteger(), nullable=False),
    sa.Column('balance_after', sa.BigInteger(), nullable=False),
    sa.Column('counterparty_user_id', sa.BigInteger(), nullable=True),
    sa.Column('admin_tg_id', sa.BigInteger(), nullable=True),
    sa.Column('user_gift_id', sa.BigInteger(), nullable=True),
    sa.Column('comment', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('amount <> 0', name=op.f('ck_star_transactions_amount_not_zero')),
    sa.ForeignKeyConstraint(['counterparty_user_id'], ['users.id'], name=op.f('fk_star_transactions_counterparty_user_id_users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_gift_id'], ['user_gifts.id'], name=op.f('fk_star_transactions_user_gift_id_user_gifts'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_star_transactions_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_star_transactions'))
    )
    op.create_index(op.f('ix_star_transactions_user_id'), 'star_transactions', ['user_id'], unique=False)
    op.create_table('message_hidden',
    sa.Column('message_id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['message_id'], ['messages.id'], name=op.f('fk_message_hidden_message_id_messages'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_message_hidden_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('message_id', 'user_id', name=op.f('pk_message_hidden'))
    )


def downgrade() -> None:
    """Удаление всех таблиц в обратном порядке."""
    op.drop_table('message_hidden')
    op.drop_index(op.f('ix_star_transactions_user_id'), table_name='star_transactions')
    op.drop_table('star_transactions')
    op.drop_index(op.f('ix_nft_transfers_nft_id'), table_name='nft_transfers')
    op.drop_table('nft_transfers')
    op.drop_index('ix_messages_chat_id_id', table_name='messages')
    op.drop_index(op.f('ix_messages_sender_id'), table_name='messages')
    op.drop_table('messages')
    op.drop_index(op.f('ix_chat_members_user_id'), table_name='chat_members')
    op.drop_table('chat_members')
    op.drop_table('user_settings')
    op.drop_index(op.f('ix_user_gifts_gift_id'), table_name='user_gifts')
    op.drop_index(op.f('ix_user_gifts_owner_id'), table_name='user_gifts')
    op.drop_table('user_gifts')
    op.drop_table('user_blocks')
    op.drop_index(op.f('ix_premium_grants_user_id'), table_name='premium_grants')
    op.drop_table('premium_grants')
    op.drop_index(op.f('ix_nft_items_collection_id'), table_name='nft_items')
    op.drop_index(op.f('ix_nft_items_owner_id'), table_name='nft_items')
    op.drop_table('nft_items')
    op.drop_index(op.f('ix_media_owner_id'), table_name='media')
    op.drop_table('media')
    op.drop_index(op.f('ix_issued_numbers_telegram_id'), table_name='issued_numbers')
    op.drop_table('issued_numbers')
    op.drop_index(op.f('ix_contacts_contact_user_id'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_owner_id'), table_name='contacts')
    op.drop_table('contacts')
    op.drop_index(op.f('ix_chats_last_message_at'), table_name='chats')
    op.drop_table('chats')
    op.drop_index(op.f('ix_auth_sessions_user_id'), table_name='auth_sessions')
    op.drop_table('auth_sessions')
    op.drop_index(op.f('ix_users_telegram_id'), table_name='users')
    op.drop_index('uq_users_username_lower', table_name='users')
    op.drop_table('users')
    op.drop_table('nft_collections')
    op.drop_table('gifts')
    op.drop_index(op.f('ix_bot_users_username'), table_name='bot_users')
    op.drop_table('bot_users')
    op.drop_index(op.f('ix_admin_audit_log_admin_tg_id'), table_name='admin_audit_log')
    op.drop_table('admin_audit_log')
