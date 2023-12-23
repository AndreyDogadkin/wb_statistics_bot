import logging

from aiogram import Router, types, F
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
from bot_keyboards.callback_datas import FavoritesCallbackData, FavoritesDeleteCallbackData
from exceptions.wb_exceptions import ForUserException
from wb_api.analytics_requests import StatisticsRequests

loger = logging.getLogger(__name__)

database = DBMethods()

get_favorite_router = Router()


@get_favorite_router.message(Command(commands='favorites'), StateFilter(default_state))
async def get_favorites_gateway(message: types.Message, state: FSMContext):
    """Установка состояния выбора номера номенклатуры из списка избранных."""

    # TODO Добавить проверку лимитов запросов и токены

    user_id = message.from_user.id
    await database.add_user(user_id)
    favorites = await database.get_user_favorites(user_id)
    if favorites:
        token_analytic = await database.get_user_analytic_token(user_id)
        await state.update_data(favorites=favorites)
        await state.update_data(token_analytic=token_analytic)
        markup = MakeMarkup.favorites_markup(favorites=favorites)
        await message.answer(
            get_favorite_message_templates['favorite_requests'],
            reply_markup=markup
        )
        await state.set_state(Favorites.get_favorite)
    else:
        await message.answer(get_favorite_message_templates['no_favorites'])
    await message.delete()


@get_favorite_router.callback_query(StateFilter(Favorites.get_favorite,
                                                Favorites.delete_favorite),
                                    F.data == 'delete_favorite')
async def set_delete_favorite_state(callback: types.CallbackQuery, state: FSMContext):
    """Выбор состояния удаления либо получения избранного."""
    state_data = await state.get_data()
    favorites = state_data.get('favorites')
    delete_flag: bool = state_data.get('delete_favorite', False)
    if not delete_flag:
        await callback.answer('Выбранный запрос будет удален.')
        await state.update_data(delete_favorite=True)
        await state.set_state(Favorites.delete_favorite)
        markup = MakeMarkup.favorites_markup(favorites=favorites, delete=True)
        await callback.message.edit_text(
            get_favorite_message_templates['del_favorite_request'],
            reply_markup=markup
        )
    else:
        await callback.answer('Отмена удаления.')
        await state.update_data(delete_favorite=False)
        await state.set_state(Favorites.get_favorite)
        markup = MakeMarkup.favorites_markup(favorites=favorites)
        await callback.message.edit_text(
            get_favorite_message_templates['favorite_requests'],
            reply_markup=markup)


@get_favorite_router.callback_query(StateFilter(Favorites.delete_favorite),
                                    FavoritesDeleteCallbackData.filter())
async def delete_favorite(
        callback: types.CallbackQuery,
        callback_data: FavoritesDeleteCallbackData,
        state: FSMContext
):
    """Удаление запроса из избранного пользователя."""
    user_id = callback.from_user.id
    index_favorites_data = callback_data.unpack(callback.data).index_in_data
    state_data = await state.get_data()
    select_del_favorite = state_data.get('favorites')[index_favorites_data]
    nm_id = select_del_favorite.nm_id
    period = select_del_favorite.period
    await database.delete_user_favorite(telegram_id=user_id, nm_id=nm_id, period=period)
    await callback.answer('Удалено')


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
    token_analytic = state_data.get('token_analytic')
    statistics = StatisticsRequests(token_analytic)

    # TODO Вынести повторяющиеся части в отдельный метод

    try:
        # TODO Вынести этот метод в хелперы
        product, answer_message = await get_user_statistics(statistics, nm_id, period)
        if product and answer_message:
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
