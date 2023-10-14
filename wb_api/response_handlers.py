import logging
from functools import wraps

from pydantic import ValidationError

from exceptions.wb_exceptions import WBApiHandleException
from .response_validate_and_parse import DataAnalyticDays

logger = logging.getLogger(__name__)


class ResponseHandlers:

    @staticmethod
    def nm_ids_handler(func):
        @wraps(func)
        async def wrapper(*args, **kwargs) -> list[tuple]:
            response: dict = await func(*args, **kwargs)
            if response.get('error') is True:
                error = response.get('errorText')
                logger.error(error)
                raise WBApiHandleException(error)
            out = []
            data: dict = response.get('data')
            if data:
                cards: list = data.get('cards')
                for card in cards:
                    vendor_code = card.get('vendorCode')
                    object_ = card.get('object')
                    nm_id = card.get('nmID')
                    out.append((vendor_code, object_, nm_id))
            return out
        return wrapper

    @staticmethod
    def analytic_detail_days_handler(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            response = await func(*args, **kwargs)
            out = []
            if response.get('data'):
                try:
                    data = DataAnalyticDays.model_validate(response)
                    out.append(data.data[0].imtName)
                    for history in data.data[0].history:
                        out.append(history.__dict__.values())
                except ValidationError as e:
                    logger.error(f'Ошибка валидации ответа: {e.json()}')
            elif response.get('error') is True:
                error = response.get('errorText')
                logger.error(error)
                raise WBApiHandleException(error)
            else:
                logger.warning(f'Нет данных при обработке значений: {args}')
            return out
        return wrapper

    @staticmethod
    def analytic_detail_period_handler(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            response = await func(*args, **kwargs)
            out = []
            data = response.get('data')
            cards = data.get('cards')
            if cards:
                cards = cards[0]
                out = [cards['object']['name']]
                statistics = cards.get('statistics')
                select_period = statistics.get('selectedPeriod')
                previous_period = statistics.get('previousPeriod')
                data_for_periods = [
                    'begin',
                    'end',
                    'ordersSumRub',
                    'ordersCount',
                    'openCardCount',
                    'addToCartCount',
                    'buyoutsCount',
                    'buyoutsSumRub',
                    'avgOrdersCountPerDay',
                    'avgPriceRub'
                ]
                out += [(select_period[i] for i in data_for_periods),
                        (previous_period[i] for i in data_for_periods)]
            elif response.get('error') is True:
                error = response.get('errorText')
                logger.error(error)
                raise WBApiHandleException(error)
            else:
                logger.warning(f'Нет данных при обработке, переданные данные: {args}')
            return out
        return wrapper
