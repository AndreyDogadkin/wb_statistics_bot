import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode

from bot_handlers import get_stats_command, save_tokens_command, start_help_commands, my_limits_command
from config_data.config import get_config
from database.methods import DBMethods

config = get_config()
dp = Dispatcher()
database = DBMethods()


async def set_default_commands(bot):
    """Добавление кнопки 'Меню' со списком команд."""
    await bot.set_my_commands(
        [
            types.BotCommand(command='help', description='❓ Как пользоваться ботом.'),
            types.BotCommand(command='my_limits', description='💯 Мои лимиты.'),
            types.BotCommand(command='token', description='🔑 Добавить/обновить токен.'),
            types.BotCommand(command='get_stats', description='📈 Получить статистику.'),
        ]
    )


async def main() -> None:
    if config.bot.TEST_SERVER:
        session = AiohttpSession(proxy='http://proxy.server:3128')
        bot = Bot(config.bot.TG_TOKEN, parse_mode=ParseMode.HTML, session=session)
    else:
        bot = Bot(config.bot.TG_TOKEN, parse_mode=ParseMode.HTML)
    dp.include_router(start_help_commands.start_help_router)
    dp.include_router(get_stats_command.get_stats_router)
    dp.include_router(save_tokens_command.save_token_router)
    dp.include_router(my_limits_command.my_limits_router)
    await set_default_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        stream=sys.stdout,
                        format='[%(levelname)s : %(name)s : line-%(lineno)s : %(asctime)s] -- %(message)s')  # noqa
    asyncio.run(main())
