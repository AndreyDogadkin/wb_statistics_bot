from dataclasses import dataclass

from environs import Env
from pydantic_settings import BaseSettings

PAGINATION_SIZE = 5


class BotSettings(BaseSettings):
    """Настройки бота."""
    TG_TOKEN: str
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
