import asyncio

from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from bot.base_messages.messages_templates import account_message_templates
from bot.keyboards import (
    AccountsCallbackData,
    AccountsEditCallbackData,
    AccountsDeleteCallbackData
)
from bot.keyboards import MakeMarkup
from bot.states import AccountsStates
from config_data.config import MAX_LEN_ACCOUNT_NAME
from database.methods import DBMethods

set_account_router = Router()

database = DBMethods()


@set_account_router.message(Command('set_account'))
async def set_account_gateway(message: types.Message, state: FSMContext):
    """Точка входа для работы с аккаунтами."""
    user_id = message.from_user.id
    user_accounts = await database.get_user_accounts(telegram_id=user_id)
    await state.update_data(user_accounts=user_accounts)
    await message.delete()
    await message.answer(
        account_message_templates['main_accounts'],
        reply_markup=MakeMarkup.account_markup(user_accounts, gateway=True)
    )
    await state.set_state(AccountsStates.change_account)


@set_account_router.callback_query(
    StateFilter(AccountsStates.change_account),
    AccountsCallbackData.filter()
)
async def change_account(
        callback: types.CallbackQuery,
        callback_data: AccountsCallbackData,
        state: FSMContext
):
    """Сменить активный аккаунт пользователя."""
    user_id = callback.from_user.id
    select_account_id = callback_data.unpack(callback.data).id
    select_account_name = callback_data.unpack(callback.data).name
    is_updated: bool = await database.change_active_account(
        telegram_id=user_id,
        select_account_id=select_account_id
    )
    user_accounts = await database.get_user_accounts(telegram_id=user_id)
    if is_updated:
        await callback.message.edit_text(
            account_message_templates['main_accounts'],
            reply_markup=MakeMarkup.account_markup(user_accounts, gateway=True)
        )
        await callback.answer(f'Активный аккаунт - "{select_account_name}"')
    else:
        await callback.answer(f'Активный аккаунт остался прежним.')
    await state.clear()
    await asyncio.sleep(0.2)
    await callback.message.delete()


@set_account_router.callback_query(
    StateFilter(AccountsStates.change_account),
    F.data == 'add'
)
async def set_add_account_state(
        callback: types.CallbackQuery,
        state: FSMContext
):
    """Получить название нового аккаунта пользователя."""
    user_id = callback.from_user.id
    in_limit: bool = await database.check_limit_accounts(user_id)
    if in_limit:
        for_edit_mess = await callback.message.edit_text(
            account_message_templates[
                'send_account_name'
            ].format(MAX_LEN_ACCOUNT_NAME),
            reply_markup=MakeMarkup.cancel_builder().as_markup()
        )
        await callback.answer('Введите название аккаунта.')
        await state.set_state(AccountsStates.add_account)
        await state.update_data(for_edit_mess=for_edit_mess)
    else:
        await callback.answer(
            account_message_templates['accounts_limit_alert'],
            show_alert=True
        )


@set_account_router.message(
    StateFilter(AccountsStates.add_account),
    F.func(lambda x: len(x.text) <= MAX_LEN_ACCOUNT_NAME)
)
async def add_new_account(message: types.Message, state: FSMContext):
    """
    Добавить новый аккаунт пользователя.
    При успешном добавлении, активным становится новый аккаунт.
    """
    state_data = await state.get_data()
    for_edit_mess: types.Message = state_data.get('for_edit_mess')
    user_id = message.from_user.id
    account_name: str = message.text.strip().capitalize()
    is_created: bool = await database.create_user_account(
        telegram_id=user_id,
        account_name=account_name
    )
    await message.delete()
    if is_created:
        await for_edit_mess.edit_text(
            account_message_templates['account_added_done']
        )
        await state.clear()
        await asyncio.sleep(7)
        await for_edit_mess.delete()
    else:
        await for_edit_mess.delete()
        for_edit_mess = await message.answer(
            account_message_templates['account_name_exists'],
            reply_markup=MakeMarkup.cancel_builder().as_markup()
        )
        await state.update_data(for_edit_mess=for_edit_mess)


@set_account_router.message(
    StateFilter(AccountsStates.add_account, AccountsStates.edit_account),
    F.func(lambda x: len(x.text) > MAX_LEN_ACCOUNT_NAME)
)
async def name_too_long(message: types.Message, state: FSMContext):
    """Обработать слишком длинное название."""
    state_data = await state.get_data()
    for_edit_mess: types.Message = state_data.get('for_edit_mess')
    await message.delete()
    await for_edit_mess.delete()
    for_edit_mess = await message.answer(
        account_message_templates[
            'account_name_to_long'
        ].format(MAX_LEN_ACCOUNT_NAME),
        reply_markup=MakeMarkup.cancel_builder().as_markup()
    )
    await state.update_data(for_edit_mess=for_edit_mess)


@set_account_router.callback_query(
    StateFilter(
        AccountsStates.change_account,
        AccountsStates.edit_account
    ),
    F.func(lambda x: x.data in ('edit', 'cancel_edit'))
)
async def set_edit_account_state(
        callback: types.CallbackQuery,
        state: FSMContext
):
    """Установка или отмена состояния редактирования аккаунта."""
    state_data = await state.get_data()
    user_accounts = state_data.get('user_accounts')
    if callback.data == 'edit':
        await callback.answer('Выберите аккаунт для редактирования.')
        await callback.message.edit_text(
            'Выберите аккаунт у которого хотите изменить название.',
            reply_markup=MakeMarkup.account_markup(user_accounts, edit=True)
        )
        await state.set_state(AccountsStates.edit_account)
    elif callback.data == 'cancel_edit':
        await callback.answer('Отмена редактирования.')
        await callback.message.edit_text(
            account_message_templates['main_accounts'],
            reply_markup=MakeMarkup.account_markup(user_accounts)
        )
        await state.set_state(AccountsStates.change_account)


@set_account_router.callback_query(
    StateFilter(AccountsStates.edit_account),
    AccountsEditCallbackData.filter()
)
async def get_editable_account(
        callback: types.CallbackQuery,
        callback_data: AccountsEditCallbackData,
        state: FSMContext
):
    """
    Получить аккаунт для редактирования.
    Запросить новое имя аккаунта.
    """
    editable_account_id = callback_data.unpack(callback.data).id
    for_edit_mess = await callback.message.edit_text(
        account_message_templates[
            'send_new_account_name'
        ].format(MAX_LEN_ACCOUNT_NAME),
        reply_markup=MakeMarkup.cancel_builder().as_markup()
    )
    await callback.answer('Введите новое имя аккаунта.')
    await state.update_data(
        editable_account_id=editable_account_id,
        for_edit_mess=for_edit_mess
    )


@set_account_router.message(StateFilter(AccountsStates.edit_account))
async def get_new_name_for_editable_account(
        message: types.Message,
        state: FSMContext
):
    """Изменить название выбранного аккаунта."""
    user_id = message.from_user.id
    new_account_name = message.text.strip().capitalize()
    state_data = await state.get_data()
    editable_account_id = state_data.get('editable_account_id')
    for_edit_mess: types.Message = state_data.get('for_edit_mess')
    is_edited = await database.change_account_name(
        telegram_id=user_id,
        account_id=editable_account_id,
        new_name=new_account_name
    )
    await message.delete()
    if is_edited:
        await for_edit_mess.edit_text(
            account_message_templates[
                'account_name_edit_done'
            ].format(new_account_name)
        )
        await state.clear()
        await asyncio.sleep(5)
        await for_edit_mess.delete()
    else:
        await for_edit_mess.delete()
        for_edit_mess = await message.answer(
            account_message_templates['account_name_exists_edit'],
            reply_markup=MakeMarkup.cancel_builder().as_markup()
        )
        await state.update_data(for_edit_mess=for_edit_mess)


@set_account_router.callback_query(
    StateFilter(
        AccountsStates.change_account,
        AccountsStates.delete_account
    ),
    F.func(lambda x: x.data in ('delete', 'cancel_delete'))
)
async def set_delete_account_state(
        callback: types.CallbackQuery,
        state: FSMContext
):
    """Установка или отмена состояния удаления аккаунта."""
    state_data = await state.get_data()
    user_accounts = state_data.get('user_accounts')
    if callback.data == 'delete':
        await callback.message.edit_text(
            account_message_templates['change_account_for delete'],
            reply_markup=MakeMarkup.account_markup(user_accounts, delete=True)
        )
        await state.set_state(AccountsStates.delete_account)
    if callback.data == 'cancel_delete':
        await callback.message.edit_text(
            account_message_templates['main_accounts'],
            reply_markup=MakeMarkup.account_markup(user_accounts)
        )
        await state.set_state(AccountsStates.change_account)


@set_account_router.callback_query(
    StateFilter(AccountsStates.delete_account),
    AccountsDeleteCallbackData.filter()
)
async def delete_account(
        callback: types.CallbackQuery,
        callback_data: AccountsDeleteCallbackData,
        state: FSMContext
):
    """Удалить аккаунта пользователя."""
    user_id = callback.from_user.id
    delete_account_id = callback_data.unpack(callback.data).id
    is_deleted = await database.delete_account(
        telegram_id=user_id,
        account_id=delete_account_id
    )
    if is_deleted:
        await callback.message.edit_text(
            account_message_templates['account_delete_done']
        )
        await state.clear()
        await asyncio.sleep(5)
        await callback.message.delete()
    else:
        await callback.answer(
            account_message_templates['cant_delete_active_account_alert'],
            show_alert=True
        )
