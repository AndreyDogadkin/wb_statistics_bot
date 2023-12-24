from aiogram.fsm.state import State, StatesGroup


class Favorites(StatesGroup):
    get_favorite = State()
    send_favorite_statistics = State()
    delete_favorite = State()
