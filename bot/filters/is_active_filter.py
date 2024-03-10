from aiogram import types
from aiogram.filters import BaseFilter

from bot.services.database import DBMethods

database = DBMethods()


class IsActiveUserFilter(BaseFilter):
    """Фильтр для активных пользователей."""

    async def __call__(self, message: types.Message):
        user_id = message.from_user.id
        user = await database.get_user(user_id)
        return user.is_active
