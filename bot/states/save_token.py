from aiogram.fsm.state import State, StatesGroup


class SaveToken(StatesGroup):
    """Состояния для сохранения токена."""
    get_token_type = State()
    get_content_token = State()
    get_analytic_token = State()
