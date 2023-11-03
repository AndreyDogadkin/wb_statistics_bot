import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from http import HTTPStatus

import aiohttp

from bot_base_messages.messages_templates import err_mess_templates
from exceptions.wb_exceptions import (WBApiResponseExceptions,
                                      IncorrectKeyException,
                                      TimeoutException,
                                      UnexpectedException, ForUserException)
from .response_handlers import ResponseHandlers
from .urls_and_payloads import wb_api_urls, wb_api_payloads

logger = logging.getLogger(__name__)  # TODO Добавить нормальное логирование ошибок


class StatisticsRequests:

    def __init__(self, wb_token):
        self.token = wb_token
        self.__headers = {'Authorization': self.token,
                          'Content-type': 'application/json',
                          'Accept': 'text/plain',
                          'Content-Encoding': 'utf-8',
                          }

    async def __get_response_post(self, url, data):
        """Сессия для получения ответа от WB API."""
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
            try:
                async with session.post(url=url, data=json.dumps(data), headers=self.__headers) as response:
                    if response.status == HTTPStatus.OK:
                        response_data = await response.json()
                        return response_data
                    if response.status == HTTPStatus.UNAUTHORIZED:
                        raise IncorrectKeyException('Ошибка авторизации.')
                    raise WBApiResponseExceptions(url=url, message=response.status)
            except TimeoutError:
                raise TimeoutException(f'Время ожидания ответа истекло.')
            except Exception as e:
                raise UnexpectedException(f'Непредвиденная ошибка. URL: {url}, err: {e}')

    @staticmethod
    def __check_errors(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                response = await func(*args, **kwargs)
                return response
            except IncorrectKeyException as e:
                logger.error(e)
                raise ForUserException(err_mess_templates['incorrect_token'])
            except TimeoutException as e:
                logger.error(e)
                raise ForUserException(err_mess_templates['timeout_error'])
            except (UnexpectedException, WBApiResponseExceptions) as e:
                logger.error(e)
                raise ForUserException(err_mess_templates['try_later'])
        return wrapper

    @__check_errors
    async def get_nm_ids(self):
        """Запрос номенклатур продавца."""
        url = wb_api_urls['get_nm_ids_url']
        data = wb_api_payloads['nm_ids_payload']
        response = await self.__get_response_post(url=url, data=data)
        return ResponseHandlers.nm_ids_handler(response)

    @__check_errors
    async def get_analytics_detail_days(self,
                                        nm_ids: list,
                                        period: int = 1,
                                        aggregation_lvl: str = 'day') -> dict:
        """Запрос статистики товара по дням."""
        url = wb_api_urls['analytic_detail_url_days']
        data = {
            'nmIDs': nm_ids,
            'period': {
                'begin': str(datetime.now().date() - timedelta(days=period)),
                'end': str(datetime.now().date())
            },
            'timezone': 'Europe/Moscow',
            'aggregationLevel': aggregation_lvl
        }
        response = await self.__get_response_post(url=url, data=data)
        return ResponseHandlers.analytic_detail_days_handler(response)

    @__check_errors
    async def get_analytic_detail_periods(self, nm_ids: list, period: int = 7):
        """Запрос статистики товара по периодам."""
        url = wb_api_urls['analytic_detail_url_periods']
        data = {
            'nmIDs': nm_ids,
            'period': {
                'begin': str(datetime.now() - timedelta(days=period)),
                'end': str(datetime.now())
            },
            'page': 1
        }
        response = await self.__get_response_post(url=url, data=data)
        return ResponseHandlers.analytic_detail_period_handler(response)

    # TODO добавить просмотр остатков товаров (В документации -> статистика -> склад)
    # TODO добавить продажи (в документации -> статистика -> продажи)
