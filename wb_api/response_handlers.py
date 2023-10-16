import logging
from functools import wraps

from pydantic import ValidationError

from exceptions.wb_exceptions import WBApiHandleException
from .response_validate_and_parse import DataStatsDays, ResponseNmIDs, CardsNmIds, ResponseStatsPeriod

logger = logging.getLogger(__name__)


class ResponseHandlers:

    @staticmethod
    def __check_error_key(response) -> None:
        if response.get('error') is True:
            error = response.get('errorText')
            logger.error(error)
            raise WBApiHandleException(error)

    @classmethod
    def nm_ids_handler(cls, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            response: dict = await func(*args, **kwargs)
            cls.__check_error_key(response)
            try:
                data: ResponseNmIDs = ResponseNmIDs.model_validate(response)
                cards: list = data.data.cards
                out: list = [None] * len(cards)
                for i, card in enumerate(cards):
                    vendor_code: CardsNmIds = card.vendorCode
                    object_: CardsNmIds = card.object
                    nm_id: CardsNmIds = card.nmID
                    out[i] = (vendor_code, object_, nm_id)
                return out
            except ValidationError as e:
                logger.error(f'Ошибка валидации ответа: {e.json()}')
        return wrapper

    @classmethod
    def analytic_detail_days_handler(cls, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            response = await func(*args, **kwargs)
            cls.__check_error_key(response)
            if response.get('data'):
                try:
                    data = DataStatsDays.model_validate(response)
                    history = data.data[0].history
                    len_out_list = (len(history) + 1)
                    out: list = [None] * len_out_list
                    out[0] = data.data[0].imtName
                    for elem in history:
                        out[len_out_list - 1] = (elem.__dict__.values())
                        len_out_list -= 1
                    return out
                except ValidationError as e:
                    logger.error(f'Ошибка валидации ответа: {e.json()}')
            else:
                logger.warning(f'Нет данных при обработке значений: {args}')
        return wrapper

    @classmethod
    def analytic_detail_period_handler(cls, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            response = await func(*args, **kwargs)
            cls.__check_error_key(response)
            if response.get('data'):
                data = ResponseStatsPeriod.model_validate(response)
                name = data.data.cards[0].object.name
                statistics = data.data.cards[0].statistics
                select_period = list(statistics.selectedPeriod.__dict__.values())
                select_period_buyouts: dict = select_period.pop()['buyoutsPercent']
                previous_period = list(statistics.previousPeriod.__dict__.values())
                previous_period_buyouts = previous_period.pop()['buyoutsPercent']
                #  TODO Изменить формат даты
                return [name, ('Выбранный период:', *select_period, select_period_buyouts),
                        ('Предыдущий период:', *previous_period, previous_period_buyouts)]
            logger.warning(f'Нет данных при обработке, переданные данные: {args}')
        return wrapper
