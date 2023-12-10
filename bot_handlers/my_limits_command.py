from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state

from bot_handlers.save_tokens_command import save_token_router
from config_data.config import REQUESTS_PER_DAY_LIMIT
from database.methods import DBMethods

database = DBMethods()

my_limits_router = Router()


@save_token_router.message(Command(commands='my_limits'), StateFilter(default_state))
async def send_user_limits(message: types.Message):
    requests_count, _ = await database.get_user_per_day_requests_count(message.from_user.id)
    await message.answer(f'📤 У вас осталось {REQUESTS_PER_DAY_LIMIT - requests_count} запросов.')
    await message.delete()
