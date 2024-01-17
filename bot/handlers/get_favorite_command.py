import logging

from aiogram import Router, types, F
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.utils import markdown

from bot.base_messages.messages_templates import (
    get_favorite_message_templates,
    err_mess_templates,
    stickers, get_stats_mess_templates,
)
from bot.helpers import get_user_statistics, to_update_limits_format
from bot.keyboards import FavoritesCallbackData, FavoritesDeleteCallbackData
from bot.keyboards import MakeMarkup
from bot.states import FavoritesStates
from database.methods import DBMethods
from exceptions.wb_exceptions import ForUserException
from wb_api.analytics_requests import StatisticsRequests

loger = logging.getLogger(__name__)

database = DBMethods()

get_favorite_router = Router()


async def send_favorites_and_update_in_state_data(
        state: FSMContext,
        callback: types.CallbackQuery | types.Message
):
    user_id = callback.from_user.id
    favorites = await database.get_user_favorites(user_id)
    markup = MakeMarkup.favorites_markup(favorites=favorites)
    if favorites:
        await callback.message.edit_text(
            get_favorite_message_templates['favorite_requests'],
            reply_markup=markup
        )
        await state.set_state(FavoritesStates.get_favorite)
    else:
        await callback.message.edit_text(
            get_favorite_message_templates['no_favorites']
        )
        await state.clear()
    await state.update_data(favorites=favorites)


@get_favorite_router.message(
    Command(commands='favorites'),
    StateFilter(default_state)
)
async def get_favorites_gateway(message: types.Message, state: FSMContext):
    """Установка состояния выбора номера номенклатуры из списка избранных."""
    user_id = message.from_user.id
    await database.add_user_if_not_exist(user_id)
    user_can_make_request, _, last_request = await (
        database.check_and_get_user_limits(user_id)
    )
    if not user_can_make_request:
        next_update_limit = to_update_limits_format(last_request)
        await message.answer_sticker(stickers['limit_requests'])
        await message.answer(
            get_stats_mess_templates["limit_requests"].format(
                next_update_limit
            )
        )
        await state.clear()
    else:
        token_analytic = await database.get_user_analytic_token(user_id)
        if token_analytic:
            favorites = await database.get_user_favorites(telegram_id=user_id)
            await state.update_data(
                token_analytic=token_analytic,
                favorites=favorites
            )
            markup = MakeMarkup.favorites_markup(favorites=favorites)
            if favorites:
                await message.answer(
                    get_favorite_message_templates['favorite_requests'],
                    reply_markup=markup
                )
                await state.set_state(FavoritesStates.get_favorite)
            else:
                await message.answer(
                    get_favorite_message_templates['no_favorites']
                )
        else:
            await message.answer(get_stats_mess_templates['save_tokens'])
            await state.clear()
        await message.delete()


@get_favorite_router.callback_query(
    StateFilter(
        FavoritesStates.get_favorite,
        FavoritesStates.delete_favorite
    ),
    F.func(lambda x: x.data in ('delete', 'cancel_delete'))
)
async def set_delete_favorite_state(
        callback: types.CallbackQuery,
        state: FSMContext
):
    """Выбор состояния удаления либо получения избранного."""
    state_data = await state.get_data()
    favorites = state_data.get('favorites')
    if favorites:
        if callback.data == 'delete':
            await callback.answer('Теперь выбранный запрос будет удален.')
            await state.update_data(delete_favorite=True)
            await state.set_state(FavoritesStates.delete_favorite)
            markup = MakeMarkup.favorites_markup(
                favorites=favorites,
                delete=True
            )
            await callback.message.edit_text(
                get_favorite_message_templates['del_favorite_request'],
                reply_markup=markup
            )
        elif callback.data == 'cancel_delete':
            await callback.answer('Отмена удаления.')
            await state.update_data(delete_favorite=False)
            await state.set_state(FavoritesStates.get_favorite)
            markup = MakeMarkup.favorites_markup(favorites=favorites)
            await callback.message.edit_text(
                get_favorite_message_templates['favorite_requests'],
                reply_markup=markup
            )
    else:
        await callback.message.edit_text(
            get_favorite_message_templates['no_favorites']
        )
        await state.clear()


@get_favorite_router.callback_query(
    StateFilter(FavoritesStates.delete_favorite),
    FavoritesDeleteCallbackData.filter()
)
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
    name = select_del_favorite.name
    nm_id = select_del_favorite.nm_id
    period = select_del_favorite.period
    await database.delete_user_favorite(
        telegram_id=user_id,
        nm_id=nm_id,
        period=period
    )
    await callback.answer(f'Запрос "{name}" удален.')
    await send_favorites_and_update_in_state_data(
        callback=callback,
        state=state
    )


@get_favorite_router.callback_query(
    StateFilter(FavoritesStates.get_favorite),
    FavoritesCallbackData.filter()
)
async def send_statistics_from_favorite(
        callback: types.CallbackQuery,
        callback_data: FavoritesCallbackData,
        state: FSMContext
):
    message_wait: types.Message = await callback.message.edit_text(
        markdown.hitalic(
            get_stats_mess_templates['make_request']
        )
    )
    user_id = callback.from_user.id
    index_in_favorites_data = callback_data.unpack(
        callback.data
    ).index_in_data
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
        product, answer_message = await get_user_statistics(
            statistics,
            nm_id,
            period
        )
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
        await message_wait.answer_sticker(
            stickers['error_try_later_sticker']
        )
        await message_wait.answer(e.message)
    except TelegramAPIError as err:
        await message_wait.delete()
        await message_wait.answer_sticker(
            stickers['error_try_later_sticker']
        )
        await message_wait.answer(err_mess_templates['telegram_error'])
        loger.error(f'{err.message}, chat_id={err.method.chat_id}')
    finally:
        await state.storage.close()
        await state.clear()
        loger.info('Состояние закрыто, хранилище очищено.')
