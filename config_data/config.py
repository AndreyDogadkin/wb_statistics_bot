import datetime
from dataclasses import dataclass
from pathlib import Path

from aiogram import types
from environs import Env
from pydantic_settings import BaseSettings

BOT_COMMANDS = [
    types.BotCommand(command='help', description='❓ Как пользоваться ботом.'),
    types.BotCommand(command='token', description='🔑 Добавить/обновить токен.'),
    types.BotCommand(command='favorites', description='⭐️ Избранные запросы.'),
    types.BotCommand(command='get_stats', description='📈 Получить статистику.'),
    types.BotCommand(command='my_limits', description='💯 Мои лимиты.'),
]

PAGINATION_SIZE = 5

REQUESTS_PER_DAY_LIMIT = 40
DAY_LIMIT = 6
DAY_LIMIT_DELTA = datetime.timedelta(hours=DAY_LIMIT)

MAX_LEN_FAVORITES = 5

BASE_DIR = Path(__file__).resolve().parent.parent

DB_TEST_PATH = BASE_DIR / 'test_database.sqlite3'


class BotSettings(BaseSettings):
    """Настройки бота."""

    TEST_SERVER: bool
    TG_TOKEN: str
    NGROK_URL: str
    ADMINS: list


class DatabaseSettings(BaseSettings):
    """Настройки базы данных."""

    DB_PROD: bool
    DB_URL_TEST: str = f'sqlite+aiosqlite:///{DB_TEST_PATH}'
    DB_URL: str
    DB_PASSWORD: str


@dataclass
class MainConfig:
    bot: BotSettings
    database: DatabaseSettings


def get_config():
    Env().read_env()
    return MainConfig(bot=BotSettings(), database=DatabaseSettings())


main_config = get_config()
