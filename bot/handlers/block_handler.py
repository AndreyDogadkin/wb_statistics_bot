from aiogram import Router, types

from bot.filters.is_active_filter import IsActiveUserFilter

block_router = Router()
block_router.message(~IsActiveUserFilter())


@block_router.message()
async def block_users_answer(message: types.Message):
    await message.delete()
    await message.answer(
        '‼️😪 Вы заблокированы, обратитесь в поддержку!\n➡️ /support'
    )
