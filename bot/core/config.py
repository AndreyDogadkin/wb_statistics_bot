import datetime
from dataclasses import dataclass
from pathlib import Path

from aiogram import types
from pydantic_settings import BaseSettings, SettingsConfigDict

from bot.core.enums import Limits

BASE_DIR = Path(__file__).resolve().parent.parent.parent

MSC_TIME_DELTA = datetime.timedelta(hours=3)
MSC_TIME_ZONE = datetime.timezone(offset=MSC_TIME_DELTA, name='msc')


BOT_COMMANDS = [
    types.BotCommand(
        command='help',
        description='❓ Как пользоваться ботом.',
    ),
    types.BotCommand(
        command='set_account',
        description='👤 Управление аккаунтами.',
    ),
    types.BotCommand(
        command='favorites',
        description='⭐️ Избранные запросы.',
    ),
    types.BotCommand(
        command='get_stats',
        description='📈 Получить статистику.',
    ),
    types.BotCommand(
        command='token',
        description='🔑 Добавить/обновить токен.',
    ),
    types.BotCommand(
        command='my_limits',
        description='💯 Мои лимиты.',
    ),
    types.BotCommand(
        command='donate',
        description='🩶 Пожертвовать на развитие.',
    ),
    types.BotCommand(
        command='cancel',
        description='↩️ Сброс состояния.',
    ),
    types.BotCommand(
        command='support',
        description='🔔 Сообщить о проблеме.',
    ),
]

DAY_LIMIT_DELTA = datetime.timedelta(hours=Limits.DAY_LIMIT.value)


class EnvBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


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
    database: DatabaseSettings
    encryption: EncryptionSettings


def get_config():
    return MainConfig(
        bot=BotSettings(),
        database=DatabaseSettings(),
        encryption=EncryptionSettings(),
    )


main_config = get_config()
