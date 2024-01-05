from aiogram.fsm.state import State, StatesGroup


class HelpStates(StatesGroup):
    """Состояния команды /help."""

    change_capter = State()
