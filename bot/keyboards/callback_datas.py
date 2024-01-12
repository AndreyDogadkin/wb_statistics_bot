from aiogram.filters.callback_data import CallbackData


class NmIdsCallbackData(CallbackData, prefix='analytics'):
    """Для выбора номенклатур."""

    nm_id: int


class AccountsCallbackData(CallbackData, prefix='accounts'):
    """Для выбора аккаунта."""

    name: str
    id: int


class AccountsEditCallbackData(AccountsCallbackData, prefix='edit_account'):
    """Для редактирования аккаунта."""

    pass


class AccountsDeleteCallbackData(AccountsCallbackData, prefix='del_account'):
    """Для удаления аккаунта."""

    pass


class FavoritesCallbackData(CallbackData, prefix='favorites'):
    """Для выбора избранного запроса."""

    index_in_data: int


class FavoritesDeleteCallbackData(
    FavoritesCallbackData,
    prefix='del_favorite'
):
    """Для удаления запроса из избранного."""

    pass


class PaginationNmIds(CallbackData, prefix='page_command'):
    """Для пагинации номенклатур."""

    command: str


class DaysCallbackData(CallbackData, prefix='days_for_stats'):
    """Для выбора периода."""

    period: int


class TokenTypeCallbackData(CallbackData, prefix='token'):
    """Для выбора типа токена."""

    token_type: str


class HelpCallbackData(CallbackData, prefix='help'):
    """Для выбора раздела инструкции."""

    command: str
