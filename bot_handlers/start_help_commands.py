from aiogram import types, F, Router
from aiogram.filters import StateFilter, CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.utils import markdown

from bot_base_messages.messages_templates import info_mess_templates, stickers
from models.methods import DBMethods

start_help_router = Router()
database = DBMethods()


@start_help_router.message(CommandStart(), StateFilter(default_state))
async def command_start_handler(message: types.Message) -> None:
    """Команда start."""
    await message.answer_sticker(stickers['start_sticker'])
    await message.answer(info_mess_templates['start'].format(markdown.hbold('@' + message.from_user.username)))
    await database.add_user(message.from_user.id)


@start_help_router.message(Command(commands='help'))  # TODO Исправить текст вывода инструкции для токенов
async def command_help_handler(message: types.Message):
    """Команда help."""
    await message.answer(info_mess_templates['help'])


@start_help_router.callback_query(~StateFilter(default_state), F.data == 'cancel')
async def close_any_state(callback: types.CallbackQuery, state: FSMContext):
    """Отмена любого состояния. """
    await callback.message.delete()
    await callback.answer('Отмена.')
    await state.clear()
