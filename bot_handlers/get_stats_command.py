from os import getenv
import logging

from aiogram import types, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.utils import markdown
from dotenv import load_dotenv

from bot_base_messages.messages_templates import get_stats_mess_templates, err_mess_templates
from bot_keyboards.keyboards import MakeMarkup, NmIdsCallbackData, DaysCallBackData
from bot_states.states import GetStats
from exceptions.wb_exceptions import WBApiResponseExceptions
from wb_api.analytics_requests import StatisticsRequests

loger = logging.getLogger(__name__)
load_dotenv()
WB_TOKEN = getenv('WB_TOKEN')  # TODO delete after tests

router = Router()


@router.message(Command(commands='get_stats'), StateFilter(default_state))
async def set_get_stats_state(message: types.Message, state: FSMContext):
    for_edit = await message.answer(text='Для выполнения операции отправьте токен WB API "Стандартный".',
                                    reply_markup=MakeMarkup.cancel_builder().as_markup())
    await state.update_data(for_edit=for_edit)
    await state.set_state(GetStats.get_token)


@router.message(StateFilter(GetStats.get_token))  # TODO add token filter
async def get_user_token_send_nm_ids(message: types.Message, state: FSMContext):
    await state.update_data(token=message.text)
    state_data: dict = await state.get_data()
    for_del_message: types.Message = state_data.get('for_edit')
    await for_del_message.delete()
    token: str = state_data.get('token')
    statistics = StatisticsRequests(WB_TOKEN)  # TODO fix token after tests (get from state.get_data)
    try:
        nm_ids: list[tuple] = await statistics.get_nm_ids()
        markup: None | types.InlineKeyboardMarkup = None
        if nm_ids:
            markup = MakeMarkup.nm_ids_markup(nm_ids)
            message_for_ids: str = markdown.hbold('Выберите товар из списка ваших номенклатур:\n\n')
            for nm in nm_ids:
                message_for_ids += get_stats_mess_templates['send_nm_ids_template'].format(*nm)
            message_for_ids += markdown.hbold(get_stats_mess_templates['plus_send_nm_ids_template'])
            await state.set_state(GetStats.get_nm_id)
        else:
            message_for_ids = 'Активных номеров номенклатур не найдено.'
        await message.answer(message_for_ids, reply_markup=markup)  # TODO pagination for nm_ids list
    except (WBApiResponseExceptions, Exception):
        await message.answer(err_mess_templates['try_later'])
    finally:
        await message.delete()


@router.callback_query(StateFilter(GetStats.get_nm_id), NmIdsCallbackData.filter())
async def set_get_period_state(callback: types.CallbackQuery, callback_data: NmIdsCallbackData, state: FSMContext):
    nm_id: int = callback_data.unpack(callback.data).nm_id
    await state.update_data(nm_id=nm_id)
    markup = MakeMarkup.periods_markup()
    await callback.message.edit_text(text=get_stats_mess_templates['set_get_period_state'], reply_markup=markup)
    await state.set_state(GetStats.get_period)


@router.callback_query(StateFilter(GetStats.get_period), DaysCallBackData.filter())
async def send_user_statistics(callback: types.CallbackQuery, callback_data: DaysCallBackData, state: FSMContext):
    message_wait: types.Message = await callback.message.edit_text(markdown.hitalic('Выполняю запрос...🕐'))
    period: int = callback_data.unpack(callback.data).period
    state_data: dict = await state.get_data()
    nm_id: int = state_data.get('nm_id')
    token: str = state_data.get('token')
    statistics = StatisticsRequests(WB_TOKEN)  # TODO fix token after tests (get from state.get_data)
    try:
        product, answer_message = await get_user_statistics(statistics, nm_id, period)
        if product and answer_message:
            await callback.answer(text=product)
            await message_wait.edit_text(answer_message)
        else:
            await callback.answer(err_mess_templates['try_later'])
    except (WBApiResponseExceptions, Exception) as e:
        loger.error(e)
        await message_wait.edit_text('Ошибка при исполнении запроса')  # TODO fix error message
    finally:
        await state.clear()


async def get_user_statistics(statistics: StatisticsRequests, nm_id: int, period: int):
    message_template = get_stats_mess_templates['send_analytic_detail_days_mess_template']
    get_stats_func = statistics.get_analytics_detail_days
    if period > 5:
        message_template = get_stats_mess_templates['send_analytic_detail_period_mess_template']
        get_stats_func = statistics.get_analytic_detail_periods
    statistics_nm_id: list = await get_stats_func(nm_ids=[nm_id], period=period)
    if statistics_nm_id:
        product: str = statistics_nm_id.pop(0)
        answer_message: str = f'Товар: {markdown.hbold(product)}.\n\n'
        for nm in statistics_nm_id:
            answer_message += message_template.format(*nm)
        return product, answer_message
