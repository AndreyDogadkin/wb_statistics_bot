from aiogram.fsm.state import State, StatesGroup


class GetStatsStates(StatesGroup):
    """Состояния для получения статистики."""
    get_token = State()
    get_nm_ids = State()
    get_period = State()
