import random

from aiogram import types, F, Router
from aiogram.filters import StateFilter, CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.utils import markdown

from bot.base.messages_templates import info_mess_templates, stickers
from bot.keyboards import MakeMarkup, HelpCallbackData
from bot.services.database import DBMethods
from bot.states import HelpStates, DeleteUserStates

start_help_router = Router()
database = DBMethods()


@start_help_router.message(CommandStart(), StateFilter(default_state))
async def command_start_handler(message: types.Message):
    """Команда start."""
    username = message.from_user.username
    first_name = message.from_user.first_name
    await message.answer_sticker(stickers['start_sticker'])
    await message.answer(
        info_mess_templates['start'].format(
            markdown.hbold('@' + username if username else first_name),
        )
    )


@start_help_router.message(Command(commands='help'))
async def command_help_handler(message: types.Message, state: FSMContext):
    """Команда help."""
    await message.answer(
        info_mess_templates['change_chapter'],
        reply_markup=MakeMarkup.help_markup(),
    )
    await state.set_state(HelpStates.change_capter)
    await message.delete()


@start_help_router.callback_query(
    StateFilter(HelpStates.change_capter), HelpCallbackData.filter()
)
async def send_help_chapter(
    callback: types.CallbackQuery,
    callback_data: HelpCallbackData,
    state: FSMContext,
):
    chapters = {
        'set_account': 'help_accounts',
        'token': 'help_token',
        'favorites': 'help_favorites',
        'get_stats': 'help_get_stats',
        'cancel': 'help_cancel',
        'delete_me': 'help_delete_me',
    }
    command = callback_data.unpack(callback.data).command
    selected_chapter = chapters[command]
    await callback.answer('📑')
    await callback.message.edit_text(info_mess_templates[selected_chapter])
    await state.clear()


@start_help_router.message(Command(commands='cancel'))
async def close_any_state_command(message: types.Message, state: FSMContext):
    """Принудительный сброс любого состояния."""
    await message.delete()
    await state.clear()
    await message.answer(info_mess_templates['cancel'])


@start_help_router.callback_query(
    ~StateFilter(default_state), F.data == 'cancel'
)
async def close_any_state_callback(
    callback: types.CallbackQuery, state: FSMContext
):
    """Отмена любого состояния."""
    await callback.message.delete()
    await state.clear()
    await callback.answer('Отмена.')


@start_help_router.message(Command(commands='delete_me'))
async def send_confirm_delete_user(message: types.Message, state: FSMContext):
    """Удаление данных пользователя."""
    random_number = random.randint(1000, 9999)
    confirm_string = f'Удалить {message.from_user.username} {random_number}'
    await message.delete()
    for_del_message = await message.answer(
        info_mess_templates['delete_user_warning'].format(confirm_string),
        reply_markup=MakeMarkup.cancel_builder().as_markup(),
    )
    await state.update_data(
        confirm_string=confirm_string, for_del_message=for_del_message
    )
    await state.set_state(DeleteUserStates.delete_user)


@start_help_router.message(StateFilter(DeleteUserStates.delete_user))
async def get_confirm_delete_user(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    confirm_string: str = state_data.get('confirm_string')
    for_del_message: types.Message = state_data.get('for_del_message')
    if confirm_string == message.text:
        is_deleted = await database.delete_user(message.from_user.id)
        if is_deleted:
            await message.answer(
                '🥲 Ваши данные успешно удалены,'
                'но мы надеемся на ваше возвращение.'
            )
        else:
            await message.answer(
                '⁉️ Не удалось выполнить удаление.\n'
                'Попробуйте повторить попытку позже.'
            )
    else:
        await message.answer(
            '⛔️ Введенное сообщение не соответствует ожидаемому.\n'
            'Удаление отменено.'
        )
    await message.delete()
    await for_del_message.delete()
    await state.clear()
