__all__ = ('AuthMiddleware', 'set_middleware', 'ThrottlingMiddleware')

from aiogram import Dispatcher

from bot.middlewares.auth import AuthMiddleware
from bot.middlewares.throttling import ThrottlingMiddleware
from bot.middlewares.logging import LoggingMiddleware


def set_middleware(dp: Dispatcher):
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())
    dp.update.outer_middleware(LoggingMiddleware())
