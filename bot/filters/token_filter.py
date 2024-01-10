from aiogram import types
from aiogram.filters import BaseFilter


class TokenFilter(BaseFilter):

    async def __call__(self, message: types.Message):
        return (360 <= len(message.text) <= 390
                and message.text.startswith('eyJhb'))
