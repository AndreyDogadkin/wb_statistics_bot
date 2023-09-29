from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class MakeCallback(CallbackData, prefix='analytics'):
    nm_id: int


class MakeMarkup:

    @staticmethod
    def nm_ids_markup(data):
        markup = InlineKeyboardBuilder()
        for day in data:
            markup.button(
                text=day[0],
                callback_data=MakeCallback(nm_id=day[-1]).pack()
            )
        markup.adjust(2)
        return markup.as_markup()
