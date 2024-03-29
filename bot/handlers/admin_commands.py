from aiogram import Router, F
from aiogram import types
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters import Command

from bot.base.messages_templates import admins_message_templates
from bot.core.config import BASE_DIR, main_config
from bot.core.loader import bot
from bot.filters.admin_filter import AdminOrSuperUserFilter
from bot.services.database import DBMethods

admin_router = Router()

database = DBMethods()


@admin_router.message(Command(commands='logs'), AdminOrSuperUserFilter())
async def get_logs_handler(message: types.Message):
    """Получить файл логов бота."""
    await message.answer_document(
        types.FSInputFile(path=BASE_DIR / 'logs/wb_bot.log')
    )


@admin_router.message(Command(commands='stats'), AdminOrSuperUserFilter())
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
    if (
        len(message_split) != 3
        or message_split[1] not in ['+', '-']
        or not message_split[2].isnumeric()
    ):
        await message.answer(
            admins_message_templates['invalid_format_set_admin']
        )
    else:
        to_admin = True if message_split[1] == '+' else False
        result = await database.set_user_is_admin(
            int(message_split[2]), to_admin
        )
        if not result:
            await message.answer('Пользователь не найден.')
        else:
            await message.answer('Операция успешна.')


@admin_router.message(
    Command(commands='block'),
    F.func(lambda x: x.from_user.id in main_config.bot.SUPER_USERS),
)
async def block_user(message: types.Message):
    """
    Заблокировать или разблокировать пользователя.
    Пример: /block + 123456789 или /block - 123456789
    """
    message_split = message.text.strip().split()
    if (
        len(message_split) != 3
        or message_split[1] not in ['+', '-']
        or not message_split[2].isnumeric()
    ):
        await message.answer(
            admins_message_templates['invalid_format_set_is_active']
        )
    else:
        block = False if message_split[1] == '+' else True
        result = await database.set_user_is_active(
            int(message_split[2]), block
        )
        if not result:
            await message.answer('Пользователь не найден.')
        else:
            block_for_mess = 'заблокирован' if not block else 'разблокирован'
            try:
                await bot.send_message(
                    chat_id=int(message_split[2]),
                    text=f'‼️ Ваш профиль {block_for_mess} администратором.',
                )
            except TelegramForbiddenError:
                pass
            await message.answer(f'Пользователь {block_for_mess}.')
