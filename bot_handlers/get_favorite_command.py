from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from database.methods import DBMethods


database = DBMethods()

get_favorite_router = Router()


@get_favorite_router.message(Command(commands='favorites'), StateFilter(default_state))
async def set_save_token_state(message: types.Message, state: FSMContext):
    """Установка состояния выбора номера номенклатуры."""
    pass
