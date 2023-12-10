from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state

from bot_base_messages.messages_templates import my_limits_mess_template
from bot_handlers.save_tokens_command import save_token_router
from config_data.config import REQUESTS_PER_DAY_LIMIT
from database.methods import DBMethods
from helpers.set_limits_format import to_update_limits_format

database = DBMethods()

my_limits_router = Router()


@save_token_router.message(Command(commands='my_limits'), StateFilter(default_state))
async def send_user_limits(message: types.Message):
    """Отправка количества оставшихся запросов и времени до обновления."""
    user_id = message.from_user.id
    await database.add_user(user_id)
    user_can_make_request, requests_count, last_request = await database.check_user_limits(user_id)
    next_update_limit = to_update_limits_format(last_request)
    requests_left = REQUESTS_PER_DAY_LIMIT - requests_count
    await message.answer(my_limits_mess_template['my_limits'].format(requests_left, next_update_limit))
    await message.delete()
