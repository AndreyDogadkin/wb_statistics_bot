import datetime
from dataclasses import dataclass
from pathlib import Path

from aiogram import types
from environs import Env
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


BOT_COMMANDS = [
    types.BotCommand(
        command='help',
        description='❓ Как пользоваться ботом.'
    ),
    types.BotCommand(
        command='set_account',
        description='🗂️ Управление аккаунтами.'
    ),
    types.BotCommand(
        command='favorites',
        description='⭐️ Избранные запросы.'
    ),
    types.BotCommand(
        command='get_stats',
        description='📈 Получить статистику.'
    ),
    types.BotCommand(
        command='token',
        description='🔑 Добавить/обновить токен.'
    ),
    types.BotCommand(
        command='my_limits',
        description='💯 Мои лимиты.'
    ),
    types.BotCommand(
        command='donate',
        description='🩶 Пожертвовать на развитие.'
    ),
    types.BotCommand(
        command='cancel',
        description='↩️ Сброс состояния.'
    ),
    types.BotCommand(
        command='support',
        description='🔔 Сообщить о проблеме.'
    )
]

PERIODS_FOR_REQUESTS = (
    ('Сегодня', 0),
    ('2 Дня', 1),
    ('3 Дня', 2),
    ('5 Дней', 4),
    ('Неделя', 7),
    ('2 Недели', 14),
    ('Месяц', 31),
    ('2 Месяца', 62),
    ('6 Месяцев', 183)
)

PAGINATION_SIZE = 5

REQUESTS_PER_DAY_LIMIT = 40
DAY_LIMIT = 6
DAY_LIMIT_DELTA = datetime.timedelta(hours=DAY_LIMIT)

MAX_LEN_FAVORITES = 5
MAX_LEN_ACCOUNTS = 3

DB_TEST_PATH = BASE_DIR / 'test_database.sqlite3'


class BotSettings(BaseSettings):
    """Настройки бота."""

    TEST_SERVER: bool
    TG_TOKEN: str
    TG_TOKEN_SUPPORT: str
    NGROK_URL: str
    ADMINS: list
    SUPPORT_ID: int


class DatabaseSettings(BaseSettings):
    """Настройки базы данных."""

    DB_PROD: bool
    DB_URL_TEST: str = f'sqlite+aiosqlite:///{DB_TEST_PATH}'
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    @property
    def db_url(self):
        return ('postgresql+asyncpg://'
                f'{self.DB_USER}:{self.DB_PASSWORD}'
                f'@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}')


class EncryptionSettings(BaseSettings):
    """Настройки шифрования."""

    ENCRYPTION_KEY: bytes


@dataclass
class MainConfig:
    bot: BotSettings
    database: DatabaseSettings
    encryption: EncryptionSettings


def get_config():
    Env().read_env()
    return MainConfig(
        bot=BotSettings(),
        database=DatabaseSettings(),
        encryption=EncryptionSettings()
    )


main_config = get_config()
