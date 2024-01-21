from typing import Any, Callable, Dict, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from database.methods import DBMethods

database = DBMethods()


class AuthMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str: Any]
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        message: Message = event
        user = message.from_user
        if not user:
            return await handler(event, data)
        await database.add_user_if_not_exist(telegram_id=user.id)
        return await handler(event, data)
