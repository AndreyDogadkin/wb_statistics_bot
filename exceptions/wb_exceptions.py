class WBApiResponseExceptions(Exception):
    """Ошибка получения ответа от WB API."""

    def __init__(self, url: str, message=''):
        self.message = message
        self.url = url

    def __str__(self):
        return f'Ошибка получения ответа url: {self.url}\n{self.message}'


class WBApiHandleException(Exception):
    """Ошибка обработки ответа от WB API."""

    def __init__(self, message: str = ''):
        self.message = message

    def __str__(self):
        return f'Ошибка подготовки ответа.\n Детали: {self.message}'


class IncorrectKeyException(Exception):
    """Ошибка 401."""
    pass


class TimeoutException(Exception):
    """Ошибка времени ожидания."""
    pass


class ForUserException(Exception):
    """Ошибка для вывода сообщения пользователю."""
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
