from dataclasses import dataclass

from environs import Env
from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    TG_TOKEN: str
    ADMINS: list


class DatabaseSettings(BaseSettings):
    DB_URL: str


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
