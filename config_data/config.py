import datetime
from dataclasses import dataclass
from pathlib import Path

from environs import Env
from pydantic_settings import BaseSettings

PAGINATION_SIZE = 5
REQUESTS_PER_DAY_LIMIT = 40
DAY_LIMIT = 6
DAY_LIMIT_DELTA = datetime.timedelta(hours=DAY_LIMIT)

BASE_DIR = Path(__file__).resolve().parent.parent


class BotSettings(BaseSettings):
    """Настройки бота."""
    TEST_SERVER: bool
    TG_TOKEN: str
    NGROK_URL: str
    ADMINS: list


class DatabaseSettings(BaseSettings):
    """Настройки базы данных."""
    DB_PROD: bool
    DB_URL_TEST: str = 'sqlite+aiosqlite:////' + str(BASE_DIR) + '/test_database.sqlite3'
    DB_URL: str
    DB_PASSWORD: str


@dataclass
class MainConfig:
    bot: BotSettings
    database: DatabaseSettings


def get_config():
    Env().read_env()
    return MainConfig(
        bot=BotSettings(),
        database=DatabaseSettings()
    )
