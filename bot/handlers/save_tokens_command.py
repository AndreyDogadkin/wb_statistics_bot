import asyncio

from aiogram import types, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from bot.base.helpers import delayed_delete
from bot.base.messages_templates import (
    save_token_mess_templates,
    err_mess_templates,
)
from bot.filters import TokenFilter
from bot.filters.is_active_filter import IsActiveUserFilter
from bot.keyboards import MakeMarkup, TokenTypeCallbackData
from bot.services.database import DBMethods
from bot.states import SaveTokenStates

database = DBMethods()

save_token_router = Router()
save_token_router.message.filter(IsActiveUserFilter())


@save_token_router.message(
    Command(commands='token'), StateFilter(default_state)
)
async def set_save_token_state(message: types.Message, state: FSMContext):
    """Запуск состояния выбора типа сохраняемого токена."""
    user_id = message.from_user.id
    account = await database.get_active_account(user_id)
    for_edit = await message.answer(
        text=save_token_mess_templates['change_token_type'],
        reply_markup=MakeMarkup.change_token_markup(account=account),
    )
    await message.delete()
    await state.update_data(for_edit=for_edit)
    await state.set_state(SaveTokenStates.get_token_type)


@save_token_router.callback_query(
    StateFilter(SaveTokenStates.get_token_type), TokenTypeCallbackData.filter()
)
async def get_token_type(
    callback: types.CallbackQuery,
    callback_data: TokenTypeCallbackData,
    state: FSMContext,
):
    """Запуск состояния ожидания выбранного типа токена."""
    state_data = await state.get_data()
    await state_data.get('for_edit').delete()
    token_type = callback_data.unpack(callback.data).token_type
    mess_for_format = ''
    if token_type == 'content':
        await state.set_state(SaveTokenStates.get_content_token)
        mess_for_format = 'Контент'
    elif token_type == 'analytic':
        await state.set_state(SaveTokenStates.get_analytic_token)
        mess_for_format = 'Аналитика'
    await callback.answer('🤫')
    for_edit = await callback.message.answer(
        save_token_mess_templates['save_token'].format(mess_for_format),
        reply_markup=MakeMarkup.cancel_builder().as_markup(),
    )
    await state.update_data(for_edit=for_edit)


@save_token_router.message(
    StateFilter(SaveTokenStates.get_content_token), TokenFilter()
)
async def save_content_token(message: types.Message, state: FSMContext):
    """Получение и сохранения токена типа 'Контент'."""
    state_data = await state.get_data()
    token = message.text
    await database.save_content_token(message.from_user.id, token)
    token_analytic = await database.get_user_analytic_token(
        message.from_user.id
    )
    message_for_edit: types.Message = state_data.get('for_edit')
    if token_analytic:
        await message_for_edit.edit_text(
            save_token_mess_templates['token_updated']
        )
    else:
        await message_for_edit.edit_text(
            save_token_mess_templates['send_token_analytic']
        )
    await state.clear()
    await message.delete()
    asyncio.create_task(delayed_delete(message_for_edit, 5))


@save_token_router.message(
    StateFilter(SaveTokenStates.get_analytic_token), TokenFilter()
)
async def save_analytic_token(message: types.Message, state: FSMContext):
    """Получение и сохранения токена типа 'Аналитика'."""
    state_data = await state.get_data()
    token = message.text
    await database.save_analytic_token(message.from_user.id, token)
    token_content = await database.get_user_content_token(message.from_user.id)
    message_for_edit: types.Message = state_data.get('for_edit')
    if token_content:
        await message_for_edit.edit_text(
            save_token_mess_templates['token_updated']
        )
    else:
        await message_for_edit.edit_text(
            save_token_mess_templates['send_token_content']
        )
    await state.clear()
    await message.delete()
    asyncio.create_task(delayed_delete(message_for_edit, 5))


@save_token_router.message(
    StateFilter(
        SaveTokenStates.get_content_token, SaveTokenStates.get_analytic_token
    )
)
async def invalid_token(message: types.Message, state: FSMContext):
    """Обработка некорректно введенного токена."""
    state_data = await state.get_data()
    for_edit: types.Message = state_data.get('for_edit')
    if for_edit:
        await for_edit.delete()
    markup = MakeMarkup.cancel_builder().as_markup()
    for_edit = await message.answer(
        text=err_mess_templates['incorrect_token'], reply_markup=markup
    )
    await state.update_data(for_edit=for_edit)
    await message.delete()
