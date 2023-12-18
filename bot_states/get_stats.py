from aiogram.fsm.state import State, StatesGroup


class GetStats(StatesGroup):
    """Состояния для получения статистики."""
    get_token = State()
    get_nm_ids = State()
    get_period = State()
