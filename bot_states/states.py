from aiogram.fsm.state import State, StatesGroup


class GetStats(StatesGroup):
	get_token = State()
	get_nm_ids = State()
	get_period = State()


class SaveToken(StatesGroup):
	get_token_type = State()
	get_token = State()
