import datetime
from dataclasses import dataclass

from environs import Env
from pydantic_settings import BaseSettings

PAGINATION_SIZE = 5
REQUESTS_PER_DAY_LIMIT = 10
DAY_LIMIT = 12
DAY_LIMIT_DELTA = datetime.timedelta(hours=DAY_LIMIT)


class BotSettings(BaseSettings):
    """Настройки бота."""
    TG_TOKEN: str
    NGROK_URL: str
    ADMINS: list


class DatabaseSettings(BaseSettings):
    """Настройки базы данных."""
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
