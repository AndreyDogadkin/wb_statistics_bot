from aiogram.fsm.state import State, StatesGroup


class GetStats(StatesGroup):
	"""Состояния для получения статистики."""
	get_token = State()
	get_nm_ids = State()
	get_period = State()


class SaveToken(StatesGroup):
	"""Состояния для сохранения токена."""
	get_token_type = State()
	get_content_token = State()
	get_analytic_token = State()
