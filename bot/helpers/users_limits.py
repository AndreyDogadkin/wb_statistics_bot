import datetime

from bot.core.config import DAY_LIMIT_DELTA


def to_update_limits_format(last_request):
    """Форматирование таймдельты для вывода пользователю."""
    now = datetime.datetime.now()
    to_next_request = last_request + DAY_LIMIT_DELTA - now
    hours = to_next_request.seconds // 3600
    minutes = to_next_request.seconds % 3600 // 60
    seconds = to_next_request.seconds % 3600 % 60
    return f'{hours} часов {minutes} минут {seconds} секунд.'
