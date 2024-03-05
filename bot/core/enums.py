from enum import IntEnum, Enum


class Pagination(IntEnum):
    """Пагинация."""

    PAGINATION_SIZE_NM_ID = 10


class Limits(IntEnum):
    """Лимиты."""

    REQUESTS_PER_DAY_LIMIT = 40
    DAY_LIMIT = 6
    MAX_LIMIT_FAVORITES = 5
    MAX_LIMIT_ACCOUNTS = 3


class Lengths(IntEnum):
    """Длины значений."""

    MAX_LEN_ACCOUNT_NAME = 20


class Periods(tuple, Enum):
    """Периоды."""

    TODAY = 'Сегодня', 0
    TWO_DAYS = '2 Дня', 1
    THREE_DAYS = '3 Дня', 2
    FIVE_DAYS = '5 Дней', 4
    WEEK = 'Неделя', 7
    TWO_WEEKS = '2 Недели', 14
    MONTH = 'Месяц', 31
    TWO_MONTH = '2 Месяца', 62
    SIX_MONTH = '6 Месяцев', 183


class MyBotCommands(tuple, Enum):
    """Команды бота."""

    HELP = 'help', '❓ Как пользоваться ботом.'
    SET_ACCOUNT = 'set_account', '👤 Управление аккаунтами.'
    FAVORITES = 'favorites', '⭐️ Избранные запросы.'
    GET_STATS = 'get_stats', '📈 Получить статистику.'
    TOKEN = 'token', '🔑 Добавить/обновить токен.'
    DONATE = 'donate', '🩶 Пожертвовать на развитие.'
    SUPPORT = 'support', '🔔 Сообщить о проблеме.'
