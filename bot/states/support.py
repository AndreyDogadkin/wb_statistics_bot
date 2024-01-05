from aiogram.fsm.state import State, StatesGroup


class SupportStates(StatesGroup):
    """Состояния для поддержки."""

    get_message_for_support = State()
