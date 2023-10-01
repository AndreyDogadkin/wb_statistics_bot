import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from config_data.config import get_config
from bot_handlers import base_users_handlers


async def set_default_commands(bot):
    """Добавление кнопки 'Меню' со списком команд."""
    await bot.set_my_commands(
        [
            types.BotCommand(command='get_stats', description='Статистика'),
        ]
    )


async def main() -> None:
    config = get_config()
    bot = Bot(config.bot.token, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(base_users_handlers.router)
    await set_default_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
