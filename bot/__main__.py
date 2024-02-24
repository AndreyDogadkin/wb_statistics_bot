import asyncio
import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from aiogram import types
from fastapi import FastAPI

from bot.core import main_config
from bot.core.loader import (
    bot,
    dp,
    set_default_commands,
    remove_commands,
    set_proxy_session,
)
from bot.handlers import get_handlers_router
from bot.middlewares import set_middleware

logger = logging.getLogger(__name__)


async def on_startup():
    logger.info('Bot starting...')
    if main_config.bot.USE_PROXY:
        await set_proxy_session()
    dp.include_router(get_handlers_router())
    set_middleware(dp=dp)
    await set_default_commands()
    logger.info(f'Bot started.')


async def on_shutdown():
    logger.info('Bot stopping...')
    await remove_commands()
    await dp.storage.close()
    await dp.fsm.storage.close()
    await bot.delete_webhook()
    await bot.session.close()
    logger.info('Bot stopped.')


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await on_startup()
    await bot.set_webhook(
        main_config.webhook.webhook_url,
        allowed_updates=dp.resolve_used_update_types(),
        secret_token=main_config.webhook.WEBHOOK_SECRET,
    )
    yield
    await on_shutdown()


app = FastAPI(lifespan=lifespan)


@app.post(main_config.webhook.WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    await dp.feed_update(bot=bot, update=telegram_update)


async def _start_polling():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await bot.delete_webhook()
    await dp.start_polling(
        bot,
        allowed_updates=dp.resolve_used_update_types(),
    )


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format='[%(levelname)s : %(name)s : line-%(lineno)s : %(asctime)s] '
        '-- %(message)s',
    )
    if main_config.webhook.USE_WEBHOOK:
        uvicorn.run(
            app,
            host=main_config.webhook.WEBHOOK_HOST,
            port=main_config.webhook.WEBHOOK_PORT,
        )
    else:
        asyncio.run(_start_polling())
