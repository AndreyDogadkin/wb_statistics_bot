from datetime import datetime

from loguru import logger
from pydantic import ValidationError

from bot.base.exceptions import ForUserException
from bot.base.messages_templates import err_mess_templates
from bot.core.enums import Pagination
from bot.services.wb_api import (
    ResponseStatsDays,
    CardsNmIds,
    ResponseStatsPeriod,
    ConversionsStatsPeriod,
    BaseResponse,
)
from bot.services.wb_api.schemas.nm_ids import DataNmIDs


class ResponseHandlers:
    @staticmethod
    def __check_error_key(data: BaseResponse) -> None:
        """Проверка поля ошибок в ответе."""
        if data.error is True:
            error = data.error_text
            logger.error(f'There are errors in the response: {error}.')
            raise ForUserException(
                err_mess_templates['response_error_field_true']
            )
        if not data.data:
            logger.warning('An empty response was received.')
            raise ForUserException(err_mess_templates['empty_response'])

    @staticmethod
    def __get_datetime_format(_datetime: str, method: str):
        """Изменить формат даты под заданный."""
        formats: dict = {
            'detail_days': '%Y-%m-%d',
            'detail_period': '%Y-%m-%d %H:%M:%S',
        }
        return datetime.strptime(_datetime, formats[method]).strftime(
            '%d.%m.%y'
        )

    @classmethod
    def nm_ids_handler(cls, response) -> list[tuple]:
        """Обработчик ответа для запроса номеров номенклатур."""
        try:
            data: DataNmIDs = DataNmIDs(**response)
            cards: list = data.cards
            out: list = []
            page: list = []
            for card in cards:
                card: CardsNmIds
                vendor_code: str = card.vendor_code
                title: str = card.title
                nm_id: int = card.nm_id
                photo: str = card.media_files[0]['big']
                page.append((vendor_code, title, nm_id, photo))
                if len(page) == Pagination.PAGINATION_SIZE_NM_ID:
                    out.append(page)
                    page = []
            if page:
                out.append(page)
            return out
        except ValidationError as e:
            logger.critical(f'Response validation error: {e.json()}')
            raise ForUserException(
                err_mess_templates['response_validation_error']
            )

    @classmethod
    def analytic_detail_days_handler(cls, response):
        """Обработчик ответа для запроса статистики товара по дням."""
        try:
            data = ResponseStatsDays.model_validate(response)
            cls.__check_error_key(data)
            history = data.data[0].history
            len_out_list = len(history) + 1
            out: list = [None] * len_out_list
            out[0] = (data.data[0].imt_name, data.data[0].vendor_code)
            for elem in history:
                elem.dt = cls.__get_datetime_format(elem.dt, 'detail_days')
                out[len_out_list - 1] = elem.__dict__.values()
                len_out_list -= 1
            return out
        except ValidationError as e:
            logger.critical(f'Response validation error: {e.json()}')
            raise ForUserException(
                err_mess_templates['response_validation_error']
            )

    @classmethod
    def analytic_detail_period_handler(cls, response):
        """Обработчик ответа для запроса статистики товара по периодам."""
        try:
            data = ResponseStatsPeriod.model_validate(response)
            cls.__check_error_key(data)
            name = data.data.cards[0].object.name
            vendor_code = data.data.cards[0].vendor_code
            statistics = data.data.cards[0].statistics
            statistics.selected_period.begin = cls.__get_datetime_format(
                statistics.selected_period.begin, 'detail_period'
            )
            statistics.selected_period.end = cls.__get_datetime_format(
                statistics.selected_period.end, 'detail_period'
            )
            statistics.previous_period.begin = cls.__get_datetime_format(
                statistics.previous_period.begin, 'detail_period'
            )
            statistics.previous_period.end = cls.__get_datetime_format(
                statistics.previous_period.end, 'detail_period'
            )
            select_period = list(statistics.selected_period.__dict__.values())
            select_period_buyouts: ConversionsStatsPeriod = select_period.pop()
            previous_period = list(
                statistics.previous_period.__dict__.values()
            )
            previous_period_buyouts: ConversionsStatsPeriod = (
                previous_period.pop()
            )
            return [
                (name, vendor_code),
                (
                    'Выбранный период:',
                    *select_period,
                    select_period_buyouts.buyout_percent,
                ),
                (
                    'Предыдущий период:',
                    *previous_period,
                    previous_period_buyouts.buyout_percent,
                ),
            ]
        except ValidationError as e:
            logger.critical(f'Response validation error: {e.json()}')
            raise ForUserException(
                err_mess_templates['response_validation_error']
            )
