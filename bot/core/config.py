import datetime
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from bot.core.enums import Limits

BASE_DIR = Path(__file__).resolve().parent.parent.parent

MSC_TIME_DELTA = datetime.timedelta(hours=3)
MSC_TIME_ZONE = datetime.timezone(offset=MSC_TIME_DELTA, name='msc')
DAY_LIMIT_DELTA = datetime.timedelta(hours=Limits.DAY_LIMIT.value)


class EnvBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


class WebhookSettings(EnvBaseSettings):
    USE_WEBHOOK: bool
    WEBHOOK_BASE_URL: str
    WEBHOOK_PATH: str
    WEBHOOK_SECRET: str
    WEBHOOK_HOST: str
    WEBHOOK_PORT: int

    @property
    def webhook_url(self) -> str:
        return f'{self.WEBHOOK_BASE_URL}{self.WEBHOOK_PATH}'


class BotSettings(EnvBaseSettings):
    """Настройки бота."""

    DEBUG: bool
    SUPER_USERS: list
    USE_PROXY: bool
    TG_TOKEN: str
    TG_TOKEN_SUPPORT: str
    SUPPORT_ID: int
    PROXY: str


class DatabaseSettings(EnvBaseSettings):
    """Настройки базы данных."""

    DB_PROD: bool
    DB_TEST_PATH: str = f'{BASE_DIR}/test_database.sqlite3'
    DB_HOST: str
    DB_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    @property
    def db_url(self):
        return (
            'postgresql+asyncpg://'
            f'{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}'
            f'@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}'
        )

    @property
    def test_db_url(self):
        return f'sqlite+aiosqlite:///{self.DB_TEST_PATH}'


class EncryptionSettings(EnvBaseSettings):
    """Настройки шифрования."""

    ENCRYPTION_KEY: bytes


class MainConfig(EnvBaseSettings):
    bot: BotSettings = BotSettings()
    webhook: WebhookSettings = WebhookSettings()
    database: DatabaseSettings = DatabaseSettings()
    encryption: EncryptionSettings = EncryptionSettings()


main_config = MainConfig()
