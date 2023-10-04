from os import getenv

from aiogram import types, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.utils import markdown
from dotenv import load_dotenv

from bot_base_messages.messages_templates import BotMessagesTemplates as Templates
from bot_keyboards.keyboards import MakeMarkup, NmIdsCallbackData, PeriodCallBackData
from bot_states.states import GetStats
from exceptions.wb_exceptions import WBApiResponseExceptions
from wb_api.analytics_requests import StatisticsRequests

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
                message_for_ids += Templates.send_nm_ids_template.format(*nm)
            message_for_ids += Templates.plus_send_nm_ids_template
            await state.set_state(GetStats.get_nm_id)
        else:
            message_for_ids = 'Активных номеров номенклатур не найдено.'
        await message.answer(message_for_ids, reply_markup=markup)  # TODO pagination for nm_ids list
    except WBApiResponseExceptions:
        await message.answer(Templates.errors['try_later'])
    finally:
        await message.delete()


@router.callback_query(StateFilter(GetStats.get_nm_id), NmIdsCallbackData.filter())
async def get_user_nm_id(callback: types.CallbackQuery, callback_data: NmIdsCallbackData, state: FSMContext):
    nm_id: int = callback_data.unpack(callback.data).nm_id
    await state.update_data(nm_id=nm_id)
    # TODO add keyboard for change period
    markup = MakeMarkup.periods_markup()
    await callback.message.edit_text(text='Выберите период для получения статистику.', reply_markup=markup)
    await state.set_state(GetStats.get_period)


@router.callback_query(StateFilter(GetStats.get_period), PeriodCallBackData.filter())
async def send_user_statistics(callback: types.CallbackQuery, callback_data: PeriodCallBackData, state: FSMContext):
    message_wait: types.Message = await callback.message.edit_text(markdown.hitalic('Выполняю запрос...'))
    period: int = callback_data.unpack(callback.data).period
    state_data: dict = await state.get_data()
    nm_id: int = state_data.get('nm_id')
    token: str = state_data.get('token')
    statistics = StatisticsRequests(WB_TOKEN)  # TODO fix token after tests (get from state.get_data)
    try:
        analytics_nm_id: list = await statistics.get_analytics_detail(nm_ids=[nm_id],
                                                                      period=period,
                                                                      aggregation_lvl='day')
        if analytics_nm_id:
            product: str = analytics_nm_id.pop(0)
            answer_message: str = f'Товар: {markdown.hbold(product)}.\n\n'
            for nm in analytics_nm_id:
                answer_message += Templates.send_analytic_detail_mess_template.format(*nm)
            await callback.answer(text=product)
            await message_wait.edit_text(answer_message)
        else:
            await callback.answer(Templates.errors['try_later'])
    except WBApiResponseExceptions:
        await message_wait.edit_text('Ошибка при исполнении запроса')  # TODO fix error message
    finally:
        await state.clear()
