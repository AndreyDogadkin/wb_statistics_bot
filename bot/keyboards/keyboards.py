from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from bot.core.enums import Periods
from bot.keyboards import (
    NmIdsCallbackData,
    PaginationNmIds,
    DaysCallbackData,
    TokenTypeCallbackData,
    FavoritesCallbackData,
    FavoritesDeleteCallbackData,
    HelpCallbackData,
    AccountsCallbackData,
    AccountsEditCallbackData,
    AccountsDeleteCallbackData,
)
from bot.models import FavoriteRequest, WBAccount


class MakeMarkup:
    """Работа с inline клавиатурами."""

    @classmethod
    def nm_ids_markup(
        cls, data, page_number: int, add_to_favorite: bool = False
    ) -> InlineKeyboardMarkup:
        """Клавиатура для вывода номенклатур пользователя."""
        markup = InlineKeyboardBuilder()
        for nm in data[page_number]:
            markup.button(
                text=nm[0], callback_data=NmIdsCallbackData(nm_id=nm[2]).pack()
            )
        markup.adjust(2)
        markup.attach(cls.__pagination_builder(page_number, len(data)))
        markup.attach(
            cls.add_to_favorite_builder(add_to_favorite=add_to_favorite)
        )
        markup.attach(cls.cancel_builder())
        return markup.as_markup()

    @classmethod
    def account_markup(
        cls,
        accounts: list[WBAccount],
        gateway: bool = False,
        edit: bool = False,
        delete: bool = False,
    ) -> InlineKeyboardMarkup:
        """Клавиатура для аккаунтов пользователя."""
        markup = InlineKeyboardBuilder()
        callback_class = AccountsCallbackData
        if edit:
            callback_class = AccountsEditCallbackData
        elif delete:
            callback_class = AccountsDeleteCallbackData
        for account in accounts:
            if account.is_now_active and gateway:
                account.name = f'❖ {account.name} ❖'
            markup.button(
                text=account.name,
                callback_data=callback_class(
                    name=account.name, id=account.id
                ).pack(),
            )
        markup.adjust(1)
        if delete:
            markup.row(
                cls.empty_button(),
                cls.empty_button(),
                cls.delete_button(delete=delete),
            )
        elif edit:
            markup.row(
                cls.empty_button(),
                cls.edit_button(edit=edit),
                cls.empty_button(),
            )
        elif len(accounts) == 1:
            markup.row(
                cls.add_button(),
                cls.edit_button(edit=edit),
                cls.empty_button(),
            )
        else:
            markup.row(
                cls.add_button(),
                cls.edit_button(edit=edit),
                cls.delete_button(delete=delete),
            )
        markup.attach(cls.cancel_builder())
        return markup.as_markup()

    @classmethod
    def favorites_markup(
        cls, favorites: list[FavoriteRequest], delete: bool = False
    ) -> InlineKeyboardMarkup:
        """Клавиатура для избранных запросов."""
        markup = InlineKeyboardBuilder()
        callback_class = (
            FavoritesCallbackData
            if not delete
            else FavoritesDeleteCallbackData
        )
        for i, favorite in enumerate(favorites):
            markup.button(
                text=favorite.name,
                callback_data=callback_class(index_in_data=i).pack(),
            )
        markup.adjust(1)
        markup.row(cls.delete_button(delete))
        markup.attach(cls.cancel_builder())
        return markup.as_markup()

    @classmethod
    def periods_markup(cls) -> InlineKeyboardMarkup:
        """Клавиатура для выбора периода получения статистики."""
        markup = InlineKeyboardBuilder()
        for period in Periods:
            markup.button(
                text=period[0],
                callback_data=DaysCallbackData(period=period[1]).pack(),
            )
        markup.adjust(3)
        markup.attach(cls.cancel_builder())
        return markup.as_markup()

    @classmethod
    def help_markup(cls) -> InlineKeyboardMarkup:
        """Клавиатура для выбора раздела инструкции."""
        commands = (
            ('Аккаунты', 'set_account'),
            ('API Ключи', 'token'),
            ('Статистика', 'get_stats'),
            ('Избранное', 'favorites'),
            ('Лимиты запросов', 'my_limits'),
            ('Сброс состояний', 'cancel'),
            ('Удаление учетной записи', 'delete_me'),
        )
        markup = InlineKeyboardBuilder()
        for command in commands:
            markup.button(
                text=command[0],
                callback_data=HelpCallbackData(command=command[1]).pack(),
            )
        markup.adjust(2)
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
    def add_to_favorite_builder(
        cls, add_to_favorite: bool = False
    ) -> InlineKeyboardBuilder:
        """Кнопка добавления в избранное."""
        text = '☆' if not add_to_favorite else '⭐️'
        markup = InlineKeyboardBuilder()
        add_to_favorite_button = InlineKeyboardButton(
            text=text, callback_data=PaginationNmIds(command='favorite').pack()
        )
        markup.row(add_to_favorite_button)
        return markup

    @classmethod
    def add_button(cls) -> InlineKeyboardButton:
        """Кнопка добавления."""
        text = '✚'
        add_button = InlineKeyboardButton(text=text, callback_data='add')
        return add_button

    @classmethod
    def edit_button(cls, edit: bool = False) -> InlineKeyboardButton:
        """Кнопка редактирования."""
        text = '✎' if not edit else '✏️'
        callback_data = 'edit' if not edit else 'cancel_edit'
        edit_button = InlineKeyboardButton(
            text=text, callback_data=callback_data
        )
        return edit_button

    @classmethod
    def delete_button(cls, delete: bool = False) -> InlineKeyboardButton:
        """Кнопка удаления."""
        text = '♲' if not delete else '♻️'
        callback_data = 'delete' if not delete else 'cancel_delete'
        delete_button = InlineKeyboardButton(
            text=text, callback_data=callback_data
        )
        return delete_button

    @classmethod
    def empty_button(cls):
        empty_button = InlineKeyboardButton(text=' ', callback_data=' ')
        return empty_button

    @classmethod
    def change_token_markup(cls, account) -> InlineKeyboardMarkup:
        """Клавиатура для выбора типа сохраняемого токена."""
        tokens = account.tokens
        text_content, text_analytic = '🔴 Контент', '🔴 Аналитика'
        if tokens:
            text_content = (
                '🟢 Контент' if tokens.wb_token_content else text_content
            )
            text_analytic = (
                '🟢 Аналитика' if tokens.wb_token_analytic else text_analytic
            )
        markup = InlineKeyboardBuilder()
        markup.button(
            text=text_content,
            callback_data=TokenTypeCallbackData(token_type='content').pack(),
        )
        markup.button(
            text=text_analytic,
            callback_data=TokenTypeCallbackData(token_type='analytic').pack(),
        )
        markup.adjust(2)
        markup.attach(cls.cancel_builder())
        return markup.as_markup()

    @classmethod
    def __pagination_builder(
        cls, page_number, page_count
    ) -> InlineKeyboardBuilder:
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
