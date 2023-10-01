from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


class NmIdsCallbackData(CallbackData, prefix='analytics'):
    nm_id: int


class PeriodCallBackData(CallbackData, prefix='period_for_stats'):
    period: int


class MakeMarkup:

    cancel_button = InlineKeyboardButton(text='Отмена ❌', callback_data='cancel')

    @classmethod
    def nm_ids_markup(cls, data):
        markup = InlineKeyboardBuilder()
        for day in data:
            markup.button(
                text=day[0],
                callback_data=NmIdsCallbackData(nm_id=day[-1]).pack()
            )
        markup.adjust(2)
        markup.row(cls.cancel_button)  # TODO handle cancel button
        return markup.as_markup()

    @classmethod
    def periods_markup(cls):
        markup = InlineKeyboardBuilder()
        markup.button(text='1 день', callback_data=PeriodCallBackData(period=0).pack())
        markup.button(text='3 дня', callback_data=PeriodCallBackData(period=2).pack())
        markup.button(text='5 дней', callback_data=PeriodCallBackData(period=4).pack())
        markup.button(text='Неделя', callback_data=PeriodCallBackData(period=7).pack())
        markup.button(text='Месяц 🔒', callback_data=PeriodCallBackData(period=31).pack())
        markup.adjust(3)
        markup.row(cls.cancel_button)
        return markup.as_markup()
