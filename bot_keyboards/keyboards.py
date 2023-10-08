from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


class NmIdsCallbackData(CallbackData, prefix='analytics'):
    nm_id: int


class DaysCallBackData(CallbackData, prefix='days_for_stats'):
    period: int


class MakeMarkup:

    @classmethod
    def nm_ids_markup(cls, data) -> InlineKeyboardMarkup:
        markup = InlineKeyboardBuilder()
        for day in data:
            markup.button(
                text=day[0],
                callback_data=NmIdsCallbackData(nm_id=day[-1]).pack()
            )
        markup.adjust(3)
        markup.attach(cls.__pagination_builder())
        markup.attach(cls.cancel_builder())
        return markup.as_markup()

    @classmethod
    def periods_markup(cls) -> InlineKeyboardMarkup:
        markup = InlineKeyboardBuilder()
        markup.button(text='1 день', callback_data=DaysCallBackData(period=0).pack())
        markup.button(text='3 дня', callback_data=DaysCallBackData(period=2).pack())
        markup.button(text='5 дней', callback_data=DaysCallBackData(period=4).pack())
        markup.button(text='Неделя', callback_data=DaysCallBackData(period=7).pack())
        markup.button(text='2 недели', callback_data=DaysCallBackData(period=14).pack())
        markup.button(text='Месяц', callback_data=DaysCallBackData(period=31).pack())
        markup.button(text='2 месяца', callback_data=DaysCallBackData(period=62).pack())
        markup.button(text='6 месяцев', callback_data=DaysCallBackData(period=180).pack())
        markup.adjust(3)
        markup.attach(cls.cancel_builder())
        return markup.as_markup()

    @classmethod
    def cancel_builder(cls) -> InlineKeyboardBuilder:
        markup = InlineKeyboardBuilder()
        cancel_button = InlineKeyboardButton(text='❌', callback_data='cancel')
        markup.row(cancel_button)
        return markup

    @classmethod
    def change_token_markup(cls):
        markup = InlineKeyboardBuilder()
        # TODO make callback data class
        markup.button(text='Стандартный', callback_data='standard_token')
        markup.button(text='Статистика', callback_data='statistics_token')
        markup.adjust(2)
        markup.attach(cls.cancel_builder())
        return markup.as_markup()

    @classmethod
    def __pagination_builder(cls) -> InlineKeyboardBuilder:
        markup = InlineKeyboardBuilder()
        prev_button = InlineKeyboardButton(text='<<', callback_data='back')
        next_button = InlineKeyboardButton(text='>>', callback_data='next')
        counter_button = InlineKeyboardButton(text='0/0', callback_data='center')
        # TODO make callback data class
        markup.row(prev_button, counter_button, next_button)
        return markup
