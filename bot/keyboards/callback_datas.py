from aiogram.filters.callback_data import CallbackData


class NmIdsCallbackData(CallbackData, prefix='analytics'):
    """Callback data для номенклатур."""

    nm_id: int


class FavoritesCallbackData(CallbackData, prefix='favorites'):

    index_in_data: int


class FavoritesDeleteCallbackData(
    FavoritesCallbackData,
    prefix='del_favorite'
):

    pass


class PaginationNmIds(CallbackData, prefix='page_command'):
    """Callback data для пагинации номенклатур."""

    command: str


class DaysCallbackData(CallbackData, prefix='days_for_stats'):
    """Callback data для периодов."""

    period: int


class TokenTypeCallbackData(CallbackData, prefix='token'):
    """Callback data для выбора типа токена."""

    token_type: str


class HelpCallbackData(CallbackData, prefix='help'):

    command: str
