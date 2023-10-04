from aiogram import types, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from bot_states.states import SaveToken
from bot_keyboards.keyboards import MakeMarkup


router = Router()


@router.message(Command(commands='token'), StateFilter(default_state))
async def set_save_token_state(message: types.Message, state: FSMContext):
    await message.answer(text='Выберите сохраняемого/обновляемого токена.',
                         reply_markup=MakeMarkup.change_token_markup())
    await state.set_state(SaveToken.get_token_type)
