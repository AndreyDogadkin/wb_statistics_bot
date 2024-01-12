import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode

from bot.handlers import (
    get_favorite_router,
    get_stats_router,
    save_token_router,
    start_help_router,
    my_limits_router,
    support_router,
    donate_router,
    set_account_router
)
from config_data import main_config
from config_data.config import BOT_COMMANDS
from database.methods import DBMethods

dp = Dispatcher()
database = DBMethods()


async def set_default_commands(bot):
    """Добавление кнопки 'Меню' со списком команд."""
    await bot.set_my_commands(BOT_COMMANDS)


async def main() -> None:
    if main_config.bot.TEST_SERVER:
        session = AiohttpSession(proxy='http://proxy.server:3128')
        bot = Bot(
            main_config.bot.TG_TOKEN,
            parse_mode=ParseMode.HTML,
            session=session)
    else:
        bot = Bot(
            main_config.bot.TG_TOKEN,
            parse_mode=ParseMode.HTML
        )
    dp.include_router(start_help_router)
    dp.include_router(get_stats_router)
    dp.include_router(save_token_router)
    dp.include_router(my_limits_router)
    dp.include_router(get_favorite_router)
    dp.include_router(support_router)
    dp.include_router(donate_router)
    dp.include_router(set_account_router)
    await set_default_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format='[%(levelname)s : %(name)s : line-%(lineno)s : %(asctime)s] -- %(message)s',  # noqa
    )
    asyncio.run(main())
