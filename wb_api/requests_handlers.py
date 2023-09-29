from functools import wraps
import logging
from exceptions.wb_exceptions import WBApiHandleException


logger = logging.getLogger(__name__)


class ResponseHandlers:

    @staticmethod
    def nm_ids_handler(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
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
    def analytic_detail_handler(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            response = await func(*args, **kwargs)
            out = []
            if response.get('data'):
                data = response.get('data')[0]
                out = [data.get('imtName')]
                history = data.get('history')
                for day in history:
                    date = day.get('dt')
                    order_sum = day.get('ordersSumRub')
                    orders_count = day.get('ordersCount')
                    open_card = day.get('openCardCount')
                    add_to_cart_count = day.get('addToCartCount')
                    buy_out_count = day.get('buyoutsCount')
                    buy_out_percent = day.get('buyoutPercent')
                    buy_outs_sum = day.get('buyoutsSumRub')
                    out.append((date, order_sum, orders_count, open_card, add_to_cart_count,
                                buy_out_count, buy_out_percent, buy_outs_sum))
            elif response.get('error') is True:
                error = response.get('errorText')
                logger.error(error)
                raise WBApiHandleException(error)
            else:
                logger.warning(f'Нет данных при обработке, переданные данные: {args}')
            return out
        return wrapper
