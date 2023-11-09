import logging
from contextlib import asynccontextmanager

import uvicorn
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from fastapi import FastAPI
from aiogram import types, Dispatcher, Bot

from bot_handlers.start_help_commands import start_help_router
from bot_handlers.get_stats_command import get_stats_router
from bot_handlers.save_tokens_command import save_token_router
from polling_main_bot import config

logger = logging.getLogger(__name__)

bot = Bot(token=config.bot.TG_TOKEN, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
WEBHOOK_PATH = f'/bot/{config.bot.TG_TOKEN}'
WEBHOOK_URL = f'{config.bot.NGROK_URL}{WEBHOOK_PATH}'


async def set_default_commands(_bot):
    """Добавление кнопки 'Меню' со списком команд."""
    await _bot.set_my_commands(
        [
            types.BotCommand(command='help', description='❓ Как пользоваться ботом.'),
            types.BotCommand(command='token', description='🔑 Добавить/обновить токен.'),
            types.BotCommand(command='get_stats', description='📈 Получить статистику.'),
        ]
    )


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(url=WEBHOOK_URL)
    dp.include_router(start_help_router)
    dp.include_router(get_stats_router)
    dp.include_router(save_token_router)
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
        format=u'[%(levelname)s : %(name)s : line-%(lineno)s : %(asctime)s] -- %(message)s',  # noqa
    )
    uvicorn.run(app)
