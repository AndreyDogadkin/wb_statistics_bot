import datetime
from dataclasses import dataclass
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from bot.core.enums import Limits

BASE_DIR = Path(__file__).resolve().parent.parent.parent

MSC_TIME_DELTA = datetime.timedelta(hours=3)
MSC_TIME_ZONE = datetime.timezone(offset=MSC_TIME_DELTA, name='msc')
DAY_LIMIT_DELTA = datetime.timedelta(hours=Limits.DAY_LIMIT.value)


BOT_COMMANDS = (
    ('help', '❓ Как пользоваться ботом.'),
    ('set_account', '👤 Управление аккаунтами.'),
    ('favorites', '⭐️ Избранные запросы.'),
    ('get_stats', '📈 Получить статистику.'),
    ('token', '🔑 Добавить/обновить токен.'),
    ('my_limits', '💯 Мои лимиты.'),
    ('donate', '🩶 Пожертвовать на развитие.'),
    ('support', '🔔 Сообщить о проблеме.'),
)


class EnvBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='../.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


class WebhookSettings(EnvBaseSettings):
    USE_WEBHOOK: bool = False
    WEBHOOK_BASE_URL: str
    WEBHOOK_PATH: str
    WEBHOOK_SECRET: str
    WEBHOOK_HOST: str
    WEBHOOK_PORT: str

    @property
    def webhook_url(self) -> str:
        return f'{self.WEBHOOK_BASE_URL}{self.WEBHOOK_PATH}'


class BotSettings(EnvBaseSettings):
    """Настройки бота."""

    TEST_SERVER: bool
    TG_TOKEN: str
    TG_TOKEN_SUPPORT: str
    NGROK_URL: str
    ADMINS: list
    SUPPORT_ID: int
    PROXY: str


class DatabaseSettings(EnvBaseSettings):
    """Настройки базы данных."""

    DB_PROD: bool
    DB_TEST_PATH: str = f'{BASE_DIR}/test_database.sqlite3'
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    @property
    def db_url(self):
        return (
            'postgresql+asyncpg://'
            f'{self.DB_USER}:{self.DB_PASSWORD}'
            f'@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        )

    @property
    def test_db_url(self):
        return f'sqlite+aiosqlite:///{self.DB_TEST_PATH}'


class EncryptionSettings(EnvBaseSettings):
    """Настройки шифрования."""

    ENCRYPTION_KEY: bytes


@dataclass
class MainConfig:
    bot: BotSettings
    webhook: WebhookSettings
    database: DatabaseSettings
    encryption: EncryptionSettings


def get_config():
    return MainConfig(
        bot=BotSettings(),
        webhook=WebhookSettings(),
        database=DatabaseSettings(),
        encryption=EncryptionSettings(),
    )


main_config = get_config()
