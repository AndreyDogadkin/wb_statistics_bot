import logging
from contextlib import asynccontextmanager

import uvicorn
from aiogram import types, Dispatcher, Bot
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from fastapi import FastAPI

from bot.core.config import BOT_COMMANDS
from bot.handlers import (
    get_favorite_router,
    get_stats_router,
    save_token_router,
    start_help_router,
    my_limits_router,
    support_router,
    donate_router,
    set_account_router,
)
from bot.middlewares import AuthMiddleware
from polling_main_bot import main_config

logger = logging.getLogger(__name__)

bot = Bot(token=main_config.bot.TG_TOKEN, parse_mode=ParseMode.HTML)

storage = MemoryStorage()

dp = Dispatcher(storage=storage)

WEBHOOK_PATH = f'/bot/{main_config.bot.TG_TOKEN}'
WEBHOOK_URL = f'{main_config.bot.NGROK_URL}{WEBHOOK_PATH}'


async def set_default_commands(_bot):
    """Добавление кнопки 'Меню' со списком команд."""
    await _bot.set_my_commands(BOT_COMMANDS)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(url=WEBHOOK_URL)
    dp.include_router(start_help_router)
    dp.include_router(get_stats_router)
    dp.include_router(save_token_router)
    dp.include_router(my_limits_router)
    dp.include_router(get_favorite_router)
    dp.include_router(support_router)
    dp.include_router(donate_router)
    dp.include_router(set_account_router)

    dp.message.middleware(AuthMiddleware())

    await set_default_commands(bot)
    logger.info('app start')
    yield
    await bot.session.close()
    logger.info('app stop')


app = FastAPI(lifespan=lifespan)


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    await dp.feed_update(bot=bot, update=telegram_update)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s : %(name)s : line-%(lineno)s : %(asctime)s] -- %(message)s',  # noqa
    )
    uvicorn.run(app)
