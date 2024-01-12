from aiogram.fsm.state import StatesGroup, State


class AccountsStates(StatesGroup):
    """Состояния работы с аккаунтами."""

    change_account = State()
    add_account = State()
    edit_account = State()
    delete_account = State()
