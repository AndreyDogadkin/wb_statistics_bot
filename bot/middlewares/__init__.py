__all__ = ('AuthMiddleware', 'set_middleware')

from aiogram import Dispatcher

from bot.middlewares.auth import AuthMiddleware


def set_middleware(dp: Dispatcher):
    dp.message.middleware(AuthMiddleware())
