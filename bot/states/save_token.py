from aiogram.fsm.state import State, StatesGroup


class SaveTokenStates(StatesGroup):
    """Состояния для сохранения токена."""
    get_token_type = State()
    get_content_token = State()
    get_analytic_token = State()
