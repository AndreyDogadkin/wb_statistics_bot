import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter, CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.utils import markdown

from bot_base_messages.messages_templates import info_mess_templates
from bot_handlers import get_stats_command, save_tokens_command
from config_data.config import get_config
from models.methods import DBMethods


dp = Dispatcher()
database = DBMethods()


async def set_default_commands(bot):
    """Добавление кнопки 'Меню' со списком команд."""
    await bot.set_my_commands(
        [
            types.BotCommand(command='help', description='Как пользоваться ботом.'),
            types.BotCommand(command='token', description='Добавить/обновить токен.(В разработке)'),
            types.BotCommand(command='get_stats', description='Получить статистику.'),
        ]
    )


@dp.message(CommandStart(), StateFilter(default_state))
async def command_start_handler(message: types.Message) -> None:
    """Команда start."""
    await message.answer_sticker('CAACAgIAAxkBAAEBjxNlNEKVb0a0gj-L-BxBs8n5FWBQ_gACbwAD29t-AAGZW1Coe5OAdDAE')
    await message.answer(info_mess_templates['start'].format(markdown.hbold(message.from_user.full_name)))
    await database.add_user(message.from_user.id)


@dp.message(Command(commands='help'))
async def command_help_handler(message: types.Message):
    """Команда help."""
    await message.answer(info_mess_templates['help'])


@dp.callback_query(~StateFilter(default_state), F.data == 'cancel')
async def close_any_state(callback: types.CallbackQuery, state: FSMContext):
    """Отмена любого состояния. """
    await callback.message.delete()
    await callback.answer('Отмена.')
    await state.clear()


async def main() -> None:
    config = get_config()
    bot = Bot(config.bot.token, parse_mode=ParseMode.HTML)
    dp.include_router(get_stats_command.router)
    dp.include_router(save_tokens_command.router)
    await set_default_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
