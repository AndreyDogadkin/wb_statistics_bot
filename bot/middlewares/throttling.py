from typing import Any, Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, throttling_limit: float = 1.0):
        self.cache = TTLCache(maxsize=10_000, ttl=throttling_limit)

    async def __call__(
        self,
        handler: Callable[[CallbackQuery, dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: dict[str, Any],
    ):
        if not isinstance(event, CallbackQuery):
            return await handler(event, data)
        if event.message.chat.id in self.cache:
            return None
        self.cache[event.message.chat.id] = None
        return await handler(event, data)
