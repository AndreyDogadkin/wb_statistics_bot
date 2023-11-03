class WBApiResponseExceptions(Exception):
    def __init__(self, url: str, message=''):
        self.message = message
        self.url = url

    def __str__(self):
        return f'Ошибка обработки ответа url: {self.url}\n{self.message}'


class UnexpectedException(Exception):
    pass


class WBApiHandleException(Exception):

    def __init__(self, message: str = ''):
        self.message = message

    def __str__(self):
        return f'Ошибка подготовки ответа.\n Детали: {self.message}'


class IncorrectKeyException(Exception):
    pass


class TimeoutException(Exception):
    pass


class ForUserException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
