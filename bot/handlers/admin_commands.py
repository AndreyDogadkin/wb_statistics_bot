from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command

from bot.base.messages_templates import admins_message_templates
from bot.core.config import BASE_DIR, main_config
from bot.filters.admin_filter import AdminFilter
from bot.services.database import DBMethods

admin_router = Router()

database = DBMethods()


@admin_router.message(Command(commands='logs'), AdminFilter())
async def get_logs_handler(message: types.Message):
    """Получить файл логов бота."""
    await message.reply_document(
        types.FSInputFile(path=BASE_DIR / 'logs/wb_bot.log')
    )


@admin_router.message(Command(commands='stats'), AdminFilter())
async def get_count_stats(message: types.Message):
    """Получить количество пользователей, токенов и аккаунтов."""
    count_stats = await database.get_users_tokens_accounts_count()
    await message.answer(
        admins_message_templates['count_stats_mess_template'].format(
            *count_stats
        )
    )


@admin_router.message(
    Command(commands='admins'),
    F.func(lambda x: x.from_user.id in main_config.bot.SUPER_USERS),
)
async def set_user_to_admin(message: types.Message):
    """
    Добавить или удалить администратора.
    Пример: /admins + 123456789 или /admins - 123456789
    """
    message_split = message.text.strip().split()
    if len(message_split) != 3 or message_split[1] not in ['+', '-']:
        await message.answer(
            admins_message_templates['invalid_format_set_admin']
        )
    else:
        to_admin = True if message_split[1] == '+' else False
        result = await database.set_user_is_admin(message_split[2], to_admin)
        if not result:
            await message.answer('Пользователь не найден.')
        else:
            await message.answer('Операция успешна.')
