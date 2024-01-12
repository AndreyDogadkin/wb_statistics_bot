import asyncio

from aiogram import Router, types
from aiogram.filters import Command

donate_router = Router()


@donate_router.message(Command('donate'))
async def donate_gateway(message: types.Message):
    """Вход для обработки пожертвований."""
    await message.delete()
    mess = await message.answer('🩶 Пожертвования будут доступны позже...')
    await asyncio.sleep(5)
    await mess.delete()
