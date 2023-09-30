from os import getenv

from aiogram import types, F, Router
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils import markdown
from dotenv import load_dotenv

from bot_base_messages.messages_templates import BotMessagesTemplates as Templates
from bot_keyboards.keyboards import MakeMarkup, MakeCallback
from bot_states.states import GetNmIdFormStateGroup
from exceptions.wb_exceptions import WBApiResponseExceptions
from wb_api.analytics_requests import StatisticsRequests

load_dotenv()
WB_TOKEN = getenv('WB_TOKEN')  # For tests

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """Команда старт."""
    await message.answer(f'Привет, {markdown.hbold(message.from_user.full_name)}!\n'
                         f'Я тестовая версия бота "WB statistics!"')


@router.message(Command(commands='nm'))
async def send_user_nm_ids(message: types.Message):
    """
    Отправка списка номенклатур пользователя выполнившего запрос.
    :param message:
    :return:
    """
    statistics = StatisticsRequests(WB_TOKEN)
    try:
        nm_ids: list[tuple] = await statistics.get_nm_ids()
        markup = None
        if nm_ids:
            markup = MakeMarkup.nm_ids_markup(nm_ids)
            message_for_ids = markdown.hbold('Ваши номенклатуры:\n\n')
            for nm in nm_ids:
                message_for_ids += Templates.send_nm_ids_template.format(*nm)
            message_for_ids += Templates.plus_send_nm_ids_template
        else:
            message_for_ids = 'Активных номеров номенклатур не найдено.'
        await message.answer(message_for_ids, reply_markup=markup)
    except WBApiResponseExceptions:
        await message.answer(Templates.errors['try_later'])


@router.callback_query(MakeCallback.filter())
async def send_analytics_callback(callback: CallbackQuery, callback_data: MakeCallback):
    message_wait = await callback.message.answer(markdown.hitalic('Выполняю запрос...'))
    nm_id = callback_data.unpack(callback.data).nm_id
    statistics = StatisticsRequests(WB_TOKEN)
    analytics_nm_id = await statistics.get_analytics_detail(nm_ids=[nm_id], period=7, aggregation_lvl='day')
    if analytics_nm_id:
        product = analytics_nm_id.pop(0)
        answer_message = f'Товар: {markdown.hbold(product)}.\n\n'
        for nm_id in analytics_nm_id:
            answer_message += Templates.send_analytic_detail_mess_template.format(*nm_id)
        await callback.answer(text=product)
        await message_wait.edit_text(answer_message)
    else:
        await callback.answer(Templates.errors['try_later'])


@router.message(Command(commands='sday'))
async def set_state_nm_ids(message: types.Message, state: FSMContext):
    await message.answer(Templates.set_state_statistics_mess_template)
    await state.set_state(GetNmIdFormStateGroup.nm_id)


@router.message(StateFilter(GetNmIdFormStateGroup.nm_id), F.text.isdigit())
async def send_analytic(message: types.Message, state: FSMContext):
    message_wait = await message.answer(markdown.hitalic('Выполняю запрос...'))
    await state.update_data(nm_id=message.text)
    statistics = StatisticsRequests(WB_TOKEN)
    data = await state.get_data()
    nm_id = int(data.get('nm_id'))
    try:
        analytic_nm_id = await statistics.get_analytics_detail([nm_id])
        if analytic_nm_id:
            analytic_message = f'Товар: {markdown.hbold(analytic_nm_id.pop(0))}.\n\n'
            for nm_id in analytic_nm_id:
                analytic_message += Templates.send_analytic_detail_mess_template.format(*nm_id)
            await message_wait.edit_text(analytic_message)
        else:
            await message_wait.edit_text(Templates.errors['check_correct'])
    except WBApiResponseExceptions:
        await message_wait.edit_text(Templates.errors['try_later'])
