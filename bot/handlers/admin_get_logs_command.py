from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command

from bot.core.config import BASE_DIR, main_config

get_logs_router = Router()


@get_logs_router.message(
    Command(commands='logs'),
    F.func(lambda x: x.from_user.id in main_config.bot.SUPER_USERS),
)
async def get_logs_handler(message: types.Message):
    """Получить файл логов бота."""
    await message.reply_document(
        types.FSInputFile(path=BASE_DIR / 'logs/wb_bot.log')
    )
