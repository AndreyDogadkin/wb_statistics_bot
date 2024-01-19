import asyncio

from aiogram import Router, Bot
from aiogram import types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from bot.base_messages.messages_templates import support_mess_templates
from bot.keyboards import MakeMarkup
from bot.states import SupportStates
from config_data import main_config

support_router = Router()

support_bot = Bot(main_config.bot.TG_TOKEN_SUPPORT)
support_id = main_config.bot.SUPPORT_ID


@support_router.message(Command('support'), StateFilter(default_state))
async def set_get_message_state(message: types.Message, state: FSMContext):
    """Установка состояния получения сообщения от пользователя."""
    message_for_edit = await message.answer(
        support_mess_templates['get_message'],
        reply_markup=MakeMarkup.cancel_builder().as_markup()
    )
    await state.update_data(message_for_edit=message_for_edit)
    await state.set_state(SupportStates.get_message_for_support)
    await message.delete()


@support_router.message(StateFilter(SupportStates.get_message_for_support))
async def get_message_to_support(message: types.Message, state: FSMContext):
    """Получение сообщения от пользователя и отправка в поддержку."""
    state_data = await state.get_data()
    message_for_edit: types.Message = state_data.get('message_for_edit')
    await send_message_to_support(message=message)
    await message_for_edit.edit_text(
        support_mess_templates['message_send']
    )
    await message.delete()
    await state.clear()
    await asyncio.sleep(5)
    await message_for_edit.delete()


async def send_message_to_support(message: types.Message):
    """Отправка сообщения о проблеме в чат поддержки."""
    support_message = support_mess_templates['message_for_support'].format(
        message.from_user.username,
        message.from_user.id,
        message.text,
        message.date.date(),
    )
    await support_bot.send_message(
        chat_id=support_id,
        text=support_message,
    )
