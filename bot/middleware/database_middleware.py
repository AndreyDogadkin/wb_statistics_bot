from typing import Callable, Any, Awaitable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from database.methods import DBMethods


class DatabaseSession(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[
                [TelegramObject, Dict[str, Any]],
                Awaitable[Any]
            ],
            event: TelegramObject,
            data: Dict[str, Any]
    ):
        data['database'] = DBMethods()
        return await handler(event, data)
