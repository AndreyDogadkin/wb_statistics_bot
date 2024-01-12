__all__ = (
    'get_favorite_router',
    'get_stats_router',
    'my_limits_router',
    'save_token_router',
    'start_help_router',
    'support_router',
    'donate_router',
    'set_account_router'
)

from bot.handlers.donate_command import donate_router
from bot.handlers.get_favorite_command import get_favorite_router
from bot.handlers.get_stats_command import get_stats_router
from bot.handlers.my_limits_command import my_limits_router
from bot.handlers.save_tokens_command import save_token_router
from bot.handlers.set_account_command import set_account_router
from bot.handlers.start_help_commands import start_help_router
from bot.handlers.support_command import support_router
