from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


class NmIdsCallbackData(CallbackData, prefix='analytics'):
    """Callback data для номенклатур."""
    nm_id: int


class PaginationNmIds(CallbackData, prefix='page_command'):
    """Callback data для пагинации номенклатур."""
    command: str


class DaysCallbackData(CallbackData, prefix='days_for_stats'):
    """Callback data для периодов."""
    period: int


class TokenTypeCallbackData(CallbackData, prefix='token'):
    """Callback data для выбора типа токена."""
    token_type: str


class MakeMarkup:
    """Создание клавиатур."""
    @classmethod
    def nm_ids_markup(cls, data, page_number: int) -> InlineKeyboardMarkup:
        """Клавиатура для вывода номенклатур пользователя."""
        markup = InlineKeyboardBuilder()
        for nm in data[page_number]:
            markup.button(
                text=nm[0],
                callback_data=NmIdsCallbackData(nm_id=nm[2]).pack()
            )
        markup.adjust(2)
        markup.attach(cls.__pagination_builder(page_number, len(data)))
        markup.attach(cls.cancel_builder())
        return markup.as_markup()

    @classmethod
    def periods_markup(cls) -> InlineKeyboardMarkup:
        """Клавиатура для выбора периода получения статистики."""
        markup = InlineKeyboardBuilder()
        markup.button(text='1 день', callback_data=DaysCallbackData(period=0).pack())
        markup.button(text='3 дня', callback_data=DaysCallbackData(period=2).pack())
        markup.button(text='5 дней', callback_data=DaysCallbackData(period=4).pack())
        markup.button(text='Неделя', callback_data=DaysCallbackData(period=7).pack())
        markup.button(text='2 недели', callback_data=DaysCallbackData(period=14).pack())
        markup.button(text='Месяц', callback_data=DaysCallbackData(period=31).pack())
        markup.button(text='2 месяца', callback_data=DaysCallbackData(period=62).pack())
        markup.button(text='6 месяцев', callback_data=DaysCallbackData(period=180).pack())
        markup.adjust(3)
        markup.attach(cls.cancel_builder())
        return markup.as_markup()

    @classmethod
    def cancel_builder(cls) -> InlineKeyboardBuilder:
        """Кнопка отмены любого состояния."""
        markup = InlineKeyboardBuilder()
        cancel_button = InlineKeyboardButton(text='❌', callback_data='cancel')
        markup.row(cancel_button)
        return markup

    @classmethod
    def change_token_markup(cls) -> InlineKeyboardMarkup:
        """Клавиатура для выбора типа сохраняемого токена."""
        markup = InlineKeyboardBuilder()
        markup.button(text='Стандартный', callback_data=TokenTypeCallbackData(token_type='standard').pack())
        markup.button(text='Статистика 🔒', callback_data=TokenTypeCallbackData(token_type='statistics').pack())
        markup.adjust(2)
        markup.attach(cls.cancel_builder())
        return markup.as_markup()

    @classmethod
    def __pagination_builder(cls, page_number, page_count) -> InlineKeyboardBuilder:
        """Кнопки для пагинации."""
        markup = InlineKeyboardBuilder()
        prev_button = InlineKeyboardButton(text='<<', callback_data=PaginationNmIds(command='prev').pack())
        next_button = InlineKeyboardButton(text='>>', callback_data=PaginationNmIds(command='next').pack())
        empty_button = InlineKeyboardButton(text=' ', callback_data=' ')
        counter_button = InlineKeyboardButton(text=f'{page_number + 1}/{page_count}', callback_data='center')
        if page_number + 1 == page_count and page_count != 1:
            markup.row(prev_button, counter_button, empty_button)
        elif page_number + 1 == page_count == 1:
            markup.row(empty_button, counter_button, empty_button)
        elif not page_number:
            markup.row(empty_button, counter_button, next_button)
        else:
            markup.row(prev_button, counter_button, next_button)
        return markup
