from dataclasses import dataclass
from environs import Env


@dataclass
class DatabaseConfig:
    pass


@dataclass
class BotConfig:

    token: str
    admins: list[int]


@dataclass
class MainConfig:

    bot: BotConfig


def get_config():
    env: Env = Env()
    env.read_env()
    return MainConfig(
        bot=BotConfig(
            token=env('TG_TOKEN'),
            admins=[]
        )
    )
