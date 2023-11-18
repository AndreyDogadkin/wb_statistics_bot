import logging

from aiogram import types, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils import markdown

from bot_base_messages.messages_templates import get_stats_mess_templates, err_mess_templates, stickers
from bot_keyboards.keyboards import MakeMarkup, NmIdsCallbackData, DaysCallbackData, PaginationNmIds
from bot_states.states import GetStats
from exceptions.wb_exceptions import ForUserException
from models.methods import DBMethods
from wb_api.analytics_requests import StatisticsRequests

loger = logging.getLogger(__name__)

database = DBMethods()

get_stats_router = Router()


@get_stats_router.message(Command(commands='get_stats'), StateFilter(default_state))
async def set_get_stats_state(message: types.Message, state: FSMContext):
    """
    Отправка номенклатур пользователю, если токен сохранен,
    иначе установка состояния получения токена
    """
    user_id = message.from_user.id
    token_content = await database.get_user_content_token(user_id)
    token_analytic = await database.get_user_analytic_token(user_id)
    if token_content and token_analytic:
        await send_nm_ids(message, state, token_content)
        await state.update_data(token_content=token_content, token_analytic=token_analytic)
    else:
        await message.answer(get_stats_mess_templates['save_tokens'])
        await message.delete()
        await state.clear()


@get_stats_router.message(StateFilter(GetStats.get_token), F.text.len() == 149)  # TODO Удалить
async def get_user_token_send_nm_ids(message: types.Message, state: FSMContext):
    """Получить токен пользователя."""
    await state.update_data(token=message.text)
    state_data: dict = await state.get_data()
    for_delete_message: types.Message = state_data.get('for_delete_message')
    if for_delete_message:
        await for_delete_message.delete()
    token: str = state_data.get('token')
    await send_nm_ids(message, state, token)


@get_stats_router.message(StateFilter(GetStats.get_token), F.text.len() != 149)  # TODO Удалить
async def incorrect_key(message: types.Message, state: FSMContext):
    """Обработка некорректно введенного токена."""
    state_data = await state.get_data()
    for_delete_message: types.Message = state_data.get('for_delete_message')
    if for_delete_message:
        await for_delete_message.delete()
    markup = MakeMarkup.cancel_builder().as_markup()
    for_delete_message = await message.answer(text=err_mess_templates['incorrect_token'], reply_markup=markup)
    await state.update_data(for_delete_message=for_delete_message)
    await message.delete()


@get_stats_router.callback_query(StateFilter(GetStats.get_nm_ids), PaginationNmIds.filter())
async def change_page_for_nm_ids(callback: types.CallbackQuery, callback_data: PaginationNmIds, state: FSMContext):
    """Отправка выбранной страницы номеров номенклатур пользователю."""
    state_data = await state.get_data()
    page_number = state_data.get('page_number')
    nm_ids = state_data.get('nm_ids')
    command = callback_data.unpack(callback.data).command
    if page_number and command == 'prev':
        await state.update_data(page_number=page_number - 1)
        await callback.answer('<<')
    elif command == 'next' and page_number < len(nm_ids):
        await state.update_data(page_number=page_number + 1)
        await callback.answer('>>')
    message, markup = await paginate_nm_ids(state)
    await callback.message.edit_text(text=message, reply_markup=markup)


async def paginate_nm_ids(state: FSMContext) -> tuple[str, InlineKeyboardMarkup]:
    """Подготовка сообщения и клавиатуры для номеров номенклатур."""
    state_data = await state.get_data()
    nm_ids = state_data.get('nm_ids')
    page_number = state_data.get('page_number')
    markup = MakeMarkup.nm_ids_markup(nm_ids, page_number)
    message_for_ids: str = markdown.hbold(get_stats_mess_templates['change_nm_id'])
    for nm in nm_ids[page_number]:
        message_for_ids += get_stats_mess_templates['send_nm_ids_template'].format(*nm)
        await state.update_data(data={f'photo:{nm[2]}': nm[3]})
    message_for_ids += markdown.hbold(get_stats_mess_templates['plus_send_nm_ids_template'])
    return message_for_ids, markup


async def send_nm_ids(message: types.Message, state: FSMContext, token_content):
    """Отправка первой страницы номеров номенклатур пользователю."""
    statistics = StatisticsRequests(token_content)
    try:
        nm_ids: list[list[tuple]] = await statistics.get_nm_ids()
        if nm_ids:
            await state.update_data(nm_ids=nm_ids)
            await state.update_data(page_number=0)
            message_for_ids, markup = await paginate_nm_ids(state)
            await state.set_state(GetStats.get_nm_ids)
            await message.answer(message_for_ids, reply_markup=markup)
        else:
            await state.clear()
            await message.answer(err_mess_templates['no_active_nms'])
    except ForUserException as e:
        await message.answer_sticker(stickers['error_try_later_sticker'])
        await message.answer(e.message)
        await state.clear()
    finally:
        await message.delete()


@get_stats_router.callback_query(StateFilter(GetStats.get_nm_ids), NmIdsCallbackData.filter())
async def set_period_state(callback: types.CallbackQuery, callback_data: NmIdsCallbackData, state: FSMContext):
    """Получения номера номенклатуры от пользователя, установка состояния получения периода."""
    nm_id: int = callback_data.unpack(callback.data).nm_id
    await state.update_data(nm_id=nm_id)
    markup = MakeMarkup.periods_markup()
    await callback.message.edit_text(text=get_stats_mess_templates['set_get_period_state'], reply_markup=markup)
    await state.set_state(GetStats.get_period)


async def get_user_statistics(statistics: StatisticsRequests, nm_id: int, period: int) -> tuple[str, str]:
    """Получить статистику пользователя."""
    message_template = get_stats_mess_templates['send_analytic_detail_days_mess_template']
    get_stats_func = statistics.get_analytics_detail_days
    if period > 5:
        message_template = get_stats_mess_templates['send_analytic_detail_period_mess_template']
        get_stats_func = statistics.get_analytic_detail_periods
    statistics_nm_id: list = await get_stats_func(nm_ids=[nm_id], period=period)
    if statistics_nm_id:
        product: str = statistics_nm_id.pop(0)
        answer_message: str = get_stats_mess_templates['product_vendor_code'].format(*product)
        for nm in statistics_nm_id:
            answer_message += message_template.format(*nm)
        return product[1], answer_message


@get_stats_router.callback_query(StateFilter(GetStats.get_period), DaysCallbackData.filter())
async def send_user_statistics(callback: types.CallbackQuery, callback_data: DaysCallbackData, state: FSMContext):
    """Отправить статистику пользователю."""
    message_wait: types.Message = await callback.message.edit_text(markdown.hitalic('Выполняю запрос...🕐'))
    period: int = callback_data.unpack(callback.data).period
    state_data: dict = await state.get_data()
    nm_id: int = state_data.get('nm_id')
    token_analytic: str = state_data.get('token_analytic')
    photo: str = state_data.get(f'photo:{nm_id}')
    statistics = StatisticsRequests(token_analytic)
    try:
        product, answer_message = await get_user_statistics(statistics, nm_id, period)
        if product and answer_message:
            await callback.answer(text=product)
            await message_wait.edit_text(answer_message + markdown.hlink(title='📸', url=photo))
        else:
            await message_wait.edit_text(err_mess_templates['no_data'])
    except ForUserException as e:
        await message_wait.delete()
        await message_wait.answer_sticker(stickers['error_try_later_sticker'])
        await message_wait.answer(e.message)
    except TelegramAPIError as err:
        loger.error(f'{err.message}, chat_id={err.method.chat_id}')
        await message_wait.delete()
        await message_wait.answer_sticker(stickers['error_try_later_sticker'])
        await message_wait.answer(err_mess_templates['telegram_error'])
    finally:
        await state.storage.close()
        await state.clear()


# TODO обработать ошибки ТГ
