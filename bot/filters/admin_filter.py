from aiogram import types
from aiogram.filters import BaseFilter

from bot.core import main_config
from bot.services.database import DBMethods

database = DBMethods()


class AdminOrSuperUserFilter(BaseFilter):
    """Фильтр для админов и суперпользователей."""
    async def __call__(self, message: types.Message):
        user_id = message.from_user.id
        user = await database.get_user(user_id)
        if not user:
            return False
        return user.is_admin or user_id in main_config.bot.SUPER_USERS
