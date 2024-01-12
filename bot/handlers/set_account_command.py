from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.keyboards import MakeMarkup
from database.methods import DBMethods

set_account_router = Router()

database = DBMethods()


@set_account_router.message(Command('set_account'))
async def set_account_gateway(message: types.Message, state: FSMContext):
    """Вход для работы с аккаунтами."""
    user_id = message.from_user.id
    user_accounts = await database.get_user_accounts(telegram_id=user_id)
    await message.delete()
    await message.answer('Ваши аккаунты:',
                         reply_markup=MakeMarkup.account_markup(user_accounts))
