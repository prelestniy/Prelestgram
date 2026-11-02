"""Конфигурация приложения. Все значения читаются из переменных окружения / файла .env."""

from functools import lru_cache

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Единый объект настроек для API и Telegram-бота."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Общие ---
    app_name: str = "Prelestgram"
    app_env: str = "prod"
    api_public_url: str = "http://localhost:8000"
    log_level: str = "INFO"

    # --- JWT ---
    secret_key: str = Field(min_length=16)
    access_token_ttl_minutes: int = 60
    refresh_token_ttl_days: int = 90

    # --- PostgreSQL ---
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "prelestgram"
    postgres_user: str = "prelestgram"
    postgres_password: str

    # --- Redis ---
    redis_url: str = "redis://redis:6379/0"

    # --- MinIO ---
    minio_endpoint: str = "minio:9000"
    minio_root_user: str
    minio_root_password: str
    minio_bucket: str = "prelestgram-media"
    minio_secure: bool = False
    max_upload_mb: int = 50

    # --- Telegram-бот ---
    bot_token: str
    # Строка вида "111,222" — разбирается в свойстве admin_ids
    admin_telegram_ids: str = ""

    # --- Авторизация ---
    phone_prefix: str = "+7000"
    phone_digits: int = 11
    auth_code_ttl_seconds: int = 300
    auth_code_max_attempts: int = 5
    auth_code_resend_seconds: int = 60

    # --- Правила экономики ---
    allow_star_transfers: bool = False
    allow_user_gift_purchase: bool = False
    allow_nft_transfers: bool = False

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        """DSN для асинхронного драйвера asyncpg."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def admin_ids(self) -> set[int]:
        """Множество Telegram ID администраторов."""
        result: set[int] = set()
        for part in self.admin_telegram_ids.split(","):
            part = part.strip()
            if part.lstrip("-").isdigit():
                result.add(int(part))
        return result

    @property
    def max_upload_bytes(self) -> int:
        """Лимит загрузки в байтах."""
        return self.max_upload_mb * 1024 * 1024

    @property
    def is_dev(self) -> bool:
        """Режим разработки включает подробные ошибки и документацию API."""
        return self.app_env.lower() == "dev"


@lru_cache
def get_settings() -> Settings:
    """Кэшированный экземпляр настроек (читается один раз за процесс)."""
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
