import asyncio

from aiogram import Router, types
from aiogram.filters import Command

from bot.base.helpers import delayed_delete

donate_router = Router()


@donate_router.message(Command('donate'))
async def donate_gateway(message: types.Message):
    """Вход для обработки пожертвований."""
    await message.delete()
    mess = await message.answer('🩶 Пожертвования будут доступны позже...')
    asyncio.create_task(delayed_delete(message=mess, delay=5))
