import logging

from aiogram import Router, types
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.utils import markdown

from bot_base_messages.messages_templates import (
    get_favorite_message_templates,
    err_mess_templates,
    stickers,
)
from bot_handlers.get_stats_command import get_user_statistics
from bot_keyboards import MakeMarkup
from bot_states import Favorites
from database.methods import DBMethods
from bot_keyboards.callback_datas import FavoritesCallbackData
from exceptions.wb_exceptions import ForUserException
from wb_api.analytics_requests import StatisticsRequests

loger = logging.getLogger(__name__)

database = DBMethods()

get_favorite_router = Router()


@get_favorite_router.message(Command(commands='favorites'), StateFilter(default_state))
async def set_save_token_state(message: types.Message, state: FSMContext):
    """Установка состояния выбора номера номенклатуры из списка избранных."""

    # TODO Добавить проверку лимитов

    user_id = message.from_user.id
    await database.add_user(user_id)
    favorites = await database.get_user_favorites(user_id)
    if favorites:
        await state.update_data(favorites=favorites)
        markup = MakeMarkup.favorites_markup(favorites=favorites)
        await message.answer(
            get_favorite_message_templates['favorite_requests'],
            reply_markup=markup
        )
        await state.set_state(Favorites.get_favorite)
    else:
        await message.answer(get_favorite_message_templates['no_favorites'])


@get_favorite_router.callback_query(StateFilter(Favorites.get_favorite),
                                    FavoritesCallbackData.filter())
async def send_statistics_from_favorite(
        callback: types.CallbackQuery,
        callback_data: FavoritesCallbackData,
        state: FSMContext
):
    message_wait: types.Message = await callback.message.edit_text(
        markdown.hitalic('Выполняю запрос...🕐')
    )
    user_id = callback.from_user.id
    index_in_favorites_data = callback_data.unpack(callback.data).index_in_data
    state_data = await state.get_data()
    select_favorite = state_data.get('favorites')[index_in_favorites_data]
    nm_id = select_favorite.nm_id
    period = select_favorite.period
    photo = select_favorite.photo_url
    token_analytic = await database.get_user_analytic_token(user_id)
    statistics = StatisticsRequests(token_analytic)

    # TODO Вынести повторяющиеся части в отдельный метод

    try:
        # TODO Вынести этот метод в хелперы
        product, answer_message = await get_user_statistics(statistics, nm_id, period)
        if product and answer_message:
            await callback.answer(text=product)
            await message_wait.edit_text(answer_message + markdown.hlink(title='📸 Открыть фото.', url=photo))
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
