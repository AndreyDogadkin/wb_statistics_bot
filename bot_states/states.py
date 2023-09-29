from aiogram.fsm.state import State, StatesGroup


class GetNmIdFormStateGroup(StatesGroup):
	nm_id = State()
