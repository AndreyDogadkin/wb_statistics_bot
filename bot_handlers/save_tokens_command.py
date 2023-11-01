from aiogram import types, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from bot_keyboards.keyboards import MakeMarkup, TokenTypeCallbackData
from bot_states.states import SaveToken
from models.methods import DBMethods
from bot_base_messages.messages_templates import save_token_mess_templates, err_mess_templates

database = DBMethods()

router = Router()


@router.message(Command(commands='token'), StateFilter(default_state))
async def set_save_token_state(message: types.Message, state: FSMContext):
    """Запуск состояния выбора типа сохраняемого токена."""
    await database.add_user(message.from_user.id)
    for_edit = await message.answer(text=save_token_mess_templates['change_token_type'],
                                    reply_markup=MakeMarkup.change_token_markup())
    await state.update_data(for_edit=for_edit)
    await state.set_state(SaveToken.get_token_type)


@router.callback_query(StateFilter(SaveToken.get_token_type), TokenTypeCallbackData.filter())
async def get_token_type(callback: types.CallbackQuery, callback_data: TokenTypeCallbackData, state: FSMContext):
    """Запуск состояния ожидания выбранного типа токена."""
    state_data = await state.get_data()
    await state_data.get('for_edit').delete()
    if callback_data.unpack(callback.data).token_type == 'standard':
        await state.set_state(SaveToken.get_standard_token)
        await callback.answer('🤫')
        for_edit = await callback.message.answer(save_token_mess_templates['input_standard_token'],
                                                 reply_markup=MakeMarkup.cancel_builder().as_markup())
        await state.update_data(for_edit=for_edit)
    else:
        #  TODO Добавить условия для добавления токена "Статистика".
        await state.clear()


@router.message(StateFilter(SaveToken.get_standard_token), F.text.len() == 149)
async def save_standard_token(message: types.Message, state: FSMContext):
    """Получение и сохранения введенного токена."""
    state_data = await state.get_data()
    token = message.text
    await database.save_standard_token(message.from_user.id, token)
    await state_data.get('for_edit').edit_text(save_token_mess_templates['token_updated'])
    await message.delete()
    await state.clear()


@router.message(StateFilter(SaveToken.get_standard_token), F.text.len() != 149)
async def invalid_token(message: types.Message, state: FSMContext):
    """Обработка некорректно введенного токена."""
    state_data = await state.get_data()
    for_edit: types.Message = state_data.get('for_edit')
    if for_edit:
        await for_edit.delete()
    markup = MakeMarkup.cancel_builder().as_markup()
    for_edit = await message.answer(text=err_mess_templates['incorrect_token'], reply_markup=markup)
    await state.update_data(for_edit=for_edit)
    await message.delete()
