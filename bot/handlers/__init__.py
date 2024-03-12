__all__ = (
    'get_favorite_router',
    'get_stats_router',
    'save_token_router',
    'start_help_router',
    'support_router',
    'donate_router',
    'set_account_router',
    'get_handlers_router',
    'admin_router',
    'block_router',
)

from aiogram import Router

from bot.handlers.admin_commands import admin_router
from bot.handlers.block_handler import block_router
from bot.handlers.donate_command import donate_router
from bot.handlers.get_favorite_command import get_favorite_router
from bot.handlers.get_stats_command import get_stats_router
from bot.handlers.save_tokens_command import save_token_router
from bot.handlers.set_account_command import set_account_router
from bot.handlers.start_help_commands import start_help_router
from bot.handlers.support_command import support_router


def get_handlers_router():
    router = Router()
    router.include_routers(
        donate_router,
        get_favorite_router,
        get_stats_router,
        save_token_router,
        set_account_router,
        start_help_router,
        support_router,
        admin_router,
        block_router,
    )
    return router
