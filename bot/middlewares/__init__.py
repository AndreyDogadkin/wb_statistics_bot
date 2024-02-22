__all__ = ('AuthMiddleware', 'set_middleware', 'ThrottlingMiddleware')

from aiogram import Dispatcher

from bot.middlewares.auth import AuthMiddleware
from bot.middlewares.throttling import ThrottlingMiddleware


def set_middleware(dp: Dispatcher):
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())
