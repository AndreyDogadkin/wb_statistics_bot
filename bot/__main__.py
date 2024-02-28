import asyncio
from contextlib import asynccontextmanager
from loguru import logger

import uvicorn
from aiogram import types
from fastapi import FastAPI

from bot.core import main_config
from bot.core.config import BASE_DIR
from bot.core.loader import (
    bot,
    dp,
    set_default_commands,
    remove_commands,
    set_proxy_session,
)
from bot.handlers import get_handlers_router
from bot.middlewares import set_middleware


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
        drop_pending_updates=True,
        allowed_updates=dp.resolve_used_update_types(),
        secret_token=main_config.webhook.WEBHOOK_SECRET,
    )
    yield
    await on_shutdown()


app = FastAPI(lifespan=lifespan)


@app.post(main_config.webhook.WEBHOOK_PATH)
@logger.catch(level='CRITICAL')
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
        drop_pending_updates=True,
    )


if __name__ == '__main__':
    logger.add(
        BASE_DIR / "logs/telegram_bot.log",
        level="DEBUG" if main_config.bot.DEBUG else "WARNING",
        format="{time} | {level} | {module}:{function}:{line} | {message}",
        rotation="100 KB",
        compression="zip",
        retention="10 days",
    )

    if main_config.webhook.USE_WEBHOOK:
        uvicorn.run(
            app,
            host=main_config.webhook.WEBHOOK_HOST,
            port=main_config.webhook.WEBHOOK_PORT,
        )
    else:
        asyncio.run(_start_polling())
