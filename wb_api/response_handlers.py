import logging
from datetime import datetime

from pydantic import ValidationError

from bot_base_messages.messages_templates import err_mess_templates
from config_data.config import PAGINATION_SIZE
from exceptions.wb_exceptions import ForUserException
from .response_validate_and_parse import ResponseStatsDays, ResponseNmIDs, CardsNmIds, ResponseStatsPeriod

logger = logging.getLogger(__name__)


class ResponseHandlers:

    @staticmethod
    def __check_error_key(data) -> None:
        """Проверка поля ошибок в ответе."""
        if data.error is True:
            error = data.errorText
            logger.error(f'В ответе присутствуют ошибки: {error}.')
            raise ForUserException(err_mess_templates['response_error_field_true'])

    @staticmethod
    def __get_datetime_format(_datetime: str, method: str):
        """Изменить формат даты под заданный."""
        formats: dict = {
            'detail_days': '%Y-%m-%d',
            'detail_period': '%Y-%m-%d %H:%M:%S'
        }
        return datetime.strptime(_datetime, formats[method]).strftime('%d.%m.%y')

    @classmethod
    def nm_ids_handler(cls, response) -> list[tuple]:
        """Обработчик ответа для запроса номеров номенклатур."""
        try:
            data: ResponseNmIDs = ResponseNmIDs.model_validate(response)
            cls.__check_error_key(data)
            cards: list = data.data.cards
            out: list = []
            page: list = []
            for card in cards:
                vendor_code: CardsNmIds = card.vendorCode
                object_: CardsNmIds = card.object
                nm_id: CardsNmIds = card.nmID
                photo: CardsNmIds = card.mediaFiles[0]
                page.append((vendor_code, object_, nm_id, photo))
                if len(page) == PAGINATION_SIZE:
                    out.append(page)
                    page = []
            if page:
                out.append(page)
            return out
        except ValidationError as e:
            logger.critical(f'Ошибка валидации ответа: {e.json()}')
            raise ForUserException(err_mess_templates['response_validation_error'])

    @classmethod
    def analytic_detail_days_handler(cls, response):
        """Обработчик ответа для запроса статистики товара по дням."""
        try:
            data = ResponseStatsDays.model_validate(response)
            cls.__check_error_key(data)
            history = data.data[0].history
            len_out_list = (len(history) + 1)
            out: list = [None] * len_out_list
            out[0] = (data.data[0].imtName, data.data[0].vendorCode)
            for elem in history:
                elem.dt = cls.__get_datetime_format(elem.dt, 'detail_days')
                out[len_out_list - 1] = (elem.__dict__.values())
                len_out_list -= 1
            return out
        except ValidationError as e:
            logger.critical(f'Ошибка валидации ответа: {e.json()}')
            raise ForUserException(err_mess_templates['response_validation_error'])

    @classmethod
    def analytic_detail_period_handler(cls, response):
        """Обработчик ответа для запроса статистики товара по периодам."""
        try:
            data = ResponseStatsPeriod.model_validate(response)
            cls.__check_error_key(data)
            name = data.data.cards[0].object.name
            vendor_code = data.data.cards[0].vendorCode
            statistics = data.data.cards[0].statistics
            statistics.selectedPeriod.begin = cls.__get_datetime_format(statistics.selectedPeriod.begin,
                                                                        'detail_period')
            statistics.selectedPeriod.end = cls.__get_datetime_format(statistics.selectedPeriod.end,
                                                                      'detail_period')
            statistics.previousPeriod.begin = cls.__get_datetime_format(statistics.previousPeriod.begin,
                                                                        'detail_period')
            statistics.previousPeriod.end = cls.__get_datetime_format(statistics.previousPeriod.end,
                                                                      'detail_period')
            select_period = list(statistics.selectedPeriod.__dict__.values())
            select_period_buyouts: dict = select_period.pop()['buyoutsPercent']
            previous_period = list(statistics.previousPeriod.__dict__.values())
            previous_period_buyouts = previous_period.pop()['buyoutsPercent']
            return [(name, vendor_code), ('Выбранный период:', *select_period, select_period_buyouts),
                    ('Предыдущий период:', *previous_period, previous_period_buyouts)]
        except ValidationError as e:
            logger.critical(f'Ошибка валидации ответа: {e.json()}')
            raise ForUserException(err_mess_templates['response_validation_error'])
