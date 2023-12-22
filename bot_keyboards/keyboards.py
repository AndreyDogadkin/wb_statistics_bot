from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from bot_keyboards.callback_datas import (NmIdsCallbackData,
                                          PaginationNmIds,
                                          DaysCallbackData,
                                          TokenTypeCallbackData,
                                          FavoritesCallbackData)
from database.models import FavoriteRequest


class MakeMarkup:
    """Создание клавиатур."""

    @classmethod
    def nm_ids_markup(cls,
                      data,
                      page_number: int,
                      add_to_favorite: bool | None = False) -> InlineKeyboardMarkup:
        """Клавиатура для вывода номенклатур пользователя."""
        markup = InlineKeyboardBuilder()
        for nm in data[page_number]:
            markup.button(
                text=nm[0], callback_data=NmIdsCallbackData(nm_id=nm[2]).pack()
            )
        markup.adjust(2)
        markup.attach(cls.__pagination_builder(page_number, len(data)))
        markup.attach(cls.add_to_favorite_builder(add_to_favorite=add_to_favorite))
        markup.attach(cls.cancel_builder())
        return markup.as_markup()

    @classmethod
    def favorites_markup(cls, favorites: list[FavoriteRequest], delete: bool = False):
        markup = InlineKeyboardBuilder()
        for i, favorite in enumerate(favorites):
            markup.button(
                text=favorite.name,
                callback_data=FavoritesCallbackData(
                    index_in_data=i
                ).pack()
            )
        markup.adjust(1)
        markup.attach(cls.delete_builder(delete))
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
        markup.button(
            text='6 месяцев', callback_data=DaysCallbackData(period=180).pack()
        )
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
    def add_to_favorite_builder(cls, add_to_favorite: bool | None):
        text = '☆' if not add_to_favorite else '⭐️'
        markup = InlineKeyboardBuilder()
        add_to_favorite_button = InlineKeyboardButton(
            text=text,
            callback_data=PaginationNmIds(command='favorite').pack()
        )
        markup.row(add_to_favorite_button)
        return markup

    @classmethod
    def delete_builder(cls, delete: bool | None):
        text = '♲' if not delete else '♻️'
        markup = InlineKeyboardBuilder()
        delete_button = InlineKeyboardButton(
            text=text,
            callback_data='delete'
        )
        markup.row(delete_button)
        return markup

    @classmethod
    def change_token_markup(cls) -> InlineKeyboardMarkup:
        """Клавиатура для выбора типа сохраняемого токена."""
        markup = InlineKeyboardBuilder()
        markup.button(
            text='Контент',
            callback_data=TokenTypeCallbackData(token_type='content').pack(),
        )
        markup.button(
            text='Аналитика',
            callback_data=TokenTypeCallbackData(token_type='analytic').pack(),
        )
        markup.adjust(2)
        markup.attach(cls.cancel_builder())
        return markup.as_markup()

    @classmethod
    def __pagination_builder(cls, page_number, page_count) -> InlineKeyboardBuilder:
        """Кнопки для пагинации."""
        markup = InlineKeyboardBuilder()
        prev_button = InlineKeyboardButton(
            text='<<', callback_data=PaginationNmIds(command='prev').pack()
        )
        next_button = InlineKeyboardButton(
            text='>>', callback_data=PaginationNmIds(command='next').pack()
        )
        empty_button = InlineKeyboardButton(text=' ', callback_data=' ')
        counter_button = InlineKeyboardButton(
            text=f'{page_number + 1}/{page_count}', callback_data='center'
        )
        if page_number + 1 == page_count and page_count != 1:
            markup.row(prev_button, counter_button, empty_button)
        elif page_number + 1 == page_count == 1:
            markup.row(empty_button, counter_button, empty_button)
        elif not page_number:
            markup.row(empty_button, counter_button, next_button)
        else:
            markup.row(prev_button, counter_button, next_button)
        return markup
