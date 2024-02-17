from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state

from bot.base_messages.messages_templates import (
    my_limits_mess_template,
    stickers,
)
from bot.core.enums import Limits
from bot.handlers.save_tokens_command import save_token_router
from bot.helpers.users_limits import to_update_limits_format
from database.methods import DBMethods

database = DBMethods()

my_limits_router = Router()


@save_token_router.message(
    Command(commands='my_limits'), StateFilter(default_state)
)
async def send_user_limits(message: types.Message):
    """Отправка количества оставшихся запросов и времени до обновления."""
    user_id = message.from_user.id
    (
        user_have_request,
        requests_count,
        _,
    ) = await database.check_and_get_user_limits(user_id)
    last_request = await database.set_user_last_request(user_id)
    next_update_limit = to_update_limits_format(last_request)
    requests_left = Limits.REQUESTS_PER_DAY_LIMIT - requests_count
    if user_have_request:
        await message.answer_sticker(stickers['have_requests'])
    else:
        await message.answer_sticker(stickers['dont_have_requests'])
    await message.answer(
        my_limits_mess_template['my_limits'].format(
            requests_left, next_update_limit
        )
    )
    await message.delete()
