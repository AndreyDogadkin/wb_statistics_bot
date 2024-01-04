import logging

from aiogram import types, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils import markdown

from bot.base_messages.messages_templates import (
    get_stats_mess_templates,
    err_mess_templates,
    stickers
)
from bot.helpers import get_user_statistics, to_update_limits_format
from bot.keyboards import (
    MakeMarkup,
    NmIdsCallbackData,
    DaysCallbackData,
    PaginationNmIds
)
from bot.states import GetStats
from database.methods import DBMethods
from exceptions.wb_exceptions import ForUserException
from wb_api.analytics_requests import StatisticsRequests

loger = logging.getLogger(__name__)

database = DBMethods()

get_stats_router = Router()


@get_stats_router.message(
    Command(commands='get_stats'),
    StateFilter(default_state)
)
async def set_get_stats_state(message: types.Message, state: FSMContext):
    """
    Отправка номенклатур пользователю, если токен сохранен.
    """
    user_id = message.from_user.id
    await database.add_user_if_not_exist(user_id)
    user_can_make_request, _, last_request = await (
        database.check_user_limits(user_id)
    )
    if not user_can_make_request:
        next_update_limit = to_update_limits_format(last_request)
        await message.answer_sticker(stickers['limit_requests'])
        await message.answer(
            get_stats_mess_templates["limit_requests"].format(
                next_update_limit
            )
        )
        await message.delete()
        await state.clear()
    else:
        tokens = await database.get_user_tokens(telegram_id=user_id)
        if tokens:
            await send_nm_ids(message, state, tokens['wb_token_content'])
            await state.update_data(
                token_content=tokens['wb_token_content'],
                token_analytic=tokens['wb_token_analytic']
            )
        else:
            await message.answer(get_stats_mess_templates['save_tokens'])
            await message.delete()
            await state.clear()


@get_stats_router.callback_query(
    StateFilter(GetStats.get_nm_ids),
    PaginationNmIds.filter()
)
async def change_page_for_nm_ids(
        callback: types.CallbackQuery,
        callback_data: PaginationNmIds,
        state: FSMContext
):
    """Отправка выбранной страницы номеров номенклатур пользователю."""
    state_data = await state.get_data()
    page_number = state_data.get('page_number')
    nm_ids = state_data.get('nm_ids')
    add_in_favorite: bool = state_data.get('add_in_favorite', False)
    command = callback_data.unpack(callback.data).command
    if page_number and command == 'prev':
        await state.update_data(page_number=page_number - 1)
        await callback.answer('<<')
    elif command == 'next' and page_number < len(nm_ids):
        await state.update_data(page_number=page_number + 1)
        await callback.answer('>>')
    elif command == 'favorite':
        if add_in_favorite:
            await state.update_data(add_in_favorite=False)
            await callback.answer('Отмена добавления запроса в избранное')
        else:
            await state.update_data(add_in_favorite=True)
            await callback.answer('Запрос будет добавлен в избранное')
    message, markup = await paginate_nm_ids(state)
    await callback.message.edit_text(text=message, reply_markup=markup)


async def paginate_nm_ids(
        state: FSMContext
) -> tuple[str, InlineKeyboardMarkup]:
    """Подготовка сообщения и клавиатуры для номеров номенклатур."""
    state_data = await state.get_data()
    nm_ids = state_data.get('nm_ids')
    page_number = state_data.get('page_number')
    add_in_favorite: bool = state_data.get('add_in_favorite', False)
    markup = MakeMarkup.nm_ids_markup(
        nm_ids,
        page_number,
        add_to_favorite=add_in_favorite
    )
    message_for_ids: str = markdown.hbold(
        get_stats_mess_templates['change_nm_id']
    )
    for nm in nm_ids[page_number]:
        message_for_ids += (
            get_stats_mess_templates['send_nm_ids_template'].format(*nm)
        )
        await state.update_data(data={f'photo:{nm[2]}': nm[3]})
    message_for_ids += (
        markdown.hbold(get_stats_mess_templates['plus_send_nm_ids_template'])
    )
    return message_for_ids, markup


async def send_nm_ids(
        message: types.Message,
        state: FSMContext,
        token_content
):
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


@get_stats_router.callback_query(
    StateFilter(GetStats.get_nm_ids),
    NmIdsCallbackData.filter()
)
async def set_period_state(
        callback: types.CallbackQuery,
        callback_data: NmIdsCallbackData,
        state: FSMContext
):
    """
    Получения номера номенклатуры от пользователя.
    Установка состояния получения периода.
    """
    nm_id: int = callback_data.unpack(callback.data).nm_id
    await state.update_data(nm_id=nm_id)
    markup = MakeMarkup.periods_markup()
    await callback.message.edit_text(
        text=get_stats_mess_templates['set_get_period_state'],
        reply_markup=markup
    )
    await state.set_state(GetStats.get_period)


@get_stats_router.callback_query(
    StateFilter(GetStats.get_period),
    DaysCallbackData.filter()
)
async def send_user_statistics(
        callback: types.CallbackQuery,
        callback_data: DaysCallbackData,
        state: FSMContext
):
    """Отправить статистику пользователю."""
    message_wait: types.Message = await callback.message.edit_text(
        markdown.hitalic(
            get_stats_mess_templates['make_request']
        )
    )
    period: int = callback_data.unpack(callback.data).period
    state_data: dict = await state.get_data()
    nm_id: int = state_data.get('nm_id')
    token_analytic: str = state_data.get('token_analytic')
    photo: str = state_data.get(f'photo:{nm_id}')
    add_in_favorite: bool | None = state_data.get('add_in_favorite')
    statistics = StatisticsRequests(token_analytic)
    user_id = callback.from_user.id
    try:
        product, answer_message = await get_user_statistics(
            statistics,
            nm_id, period
        )
        if product and answer_message:
            if add_in_favorite:
                await database.add_favorite_request(
                    telegram_id=user_id,
                    name=f'{product}, дней- {period + 1}.',
                    nm_id=nm_id,
                    period=period,
                    photo_url=photo
                )
            await callback.answer(text=product)
            await message_wait.edit_text(
                answer_message + markdown.hlink(
                    title='📸 Открыть фото.',
                    url=photo
                )
            )
            await database.set_user_last_request(user_id)
            await database.set_plus_one_to_user_requests_per_day(user_id)
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
        loger.info(f'Состояние закрыто, хранилище очищено.')

# TODO обработать ошибки ТГ
