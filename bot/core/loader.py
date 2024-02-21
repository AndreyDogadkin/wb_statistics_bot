from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault

from bot.core.config import main_config
from bot.core.enums import MyBotCommands

token = main_config.bot.TG_TOKEN


bot = Bot(token=token, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


async def set_proxy_session():
    session = AiohttpSession(proxy=main_config.bot.PROXY)
    bot.session = session


async def set_default_commands(
    commands: MyBotCommands = MyBotCommands,
):
    """Добавление кнопки 'Меню' со списком команд."""
    commands = [BotCommand(command=c, description=d) for c, d in commands]
    await bot.set_my_commands(
        commands=commands,
        scope=BotCommandScopeDefault(),
    )


async def remove_commands():
    await bot.delete_my_commands(scope=BotCommandScopeDefault())
