import asyncio
import sys

from bot.core import main_config
from bot.handlers import get_handlers_router
from bot.core.loader import bot, dp, set_default_commands, remove_commands
from bot.middlewares import set_middleware
import logging

logger = logging.getLogger(__name__)


if main_config.webhook.USE_WEBHOOK:
    from aiogram.webhook.aiohttp_server import (
        SimpleRequestHandler,
        setup_application,
    )
    from aiohttp import web


async def on_startup():
    logger.info('bot starting...')

    dp.include_router(get_handlers_router())
    set_middleware(dp=dp)
    await set_default_commands()

    logger.info(f'bot started.')


async def on_shutdown():
    logger.info('bot stopping ...')

    await remove_commands()
    await dp.storage.close()
    await dp.fsm.storage.close()
    await bot.delete_webhook()
    await bot.session.close()

    logger.info('bot stopped.')


async def setup_webhook():
    await bot.set_webhook(
        main_config.webhook.webhook_url,
        allowed_updates=dp.resolve_used_update_types(),
        secret_token=main_config.webhook.WEBHOOK_SECRET,
    )

    app = web.Application()

    webhook_handler = SimpleRequestHandler(
        dispatcher=dp, bot=bot, secret_token=main_config.webhook.WEBHOOK_SECRET
    )
    webhook_handler.register(app, path=main_config.webhook.WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(
        runner=runner,
        host=main_config.webhook.WEBHOOK_HOST,
        port=main_config.webhook.WEBHOOK_PORT,
    )
    await site.start()
    await asyncio.Event().wait()


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    if main_config.webhook.USE_WEBHOOK:
        await setup_webhook()
    else:
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
    asyncio.run(main())
