import asyncio
import json
from datetime import datetime, timedelta
from functools import wraps
from http import HTTPStatus
from time import time
from typing import Coroutine

import aiohttp
from loguru import logger

from bot.base.exceptions import (
    WBApiResponseExceptions,
    IncorrectKeyException,
    TimeoutException,
    ForUserException,
    ToManyRequestsException,
)
from bot.base.messages_templates import err_mess_templates
from bot.core import main_config, MSC_TIME_ZONE, MSC_TIME_DELTA
from bot.services.wb_api import ResponseHandlers
from bot.services.wb_api.urls_and_payloads import WBApiUrls, WBApiPayloads


class StatisticsRequests:
    def __init__(self, wb_token):
        self.token = wb_token
        self.__headers = {
            'Authorization': self.token,
            'Content-type': 'application/json',
            'Accept': '*/*',
            'Content-Encoding': 'utf-8',
        }

    async def __get_response_post(self, url, data):
        """Сессия для получения ответа от WB API."""
        proxy = main_config.bot.PROXY if main_config.bot.USE_PROXY else ''

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            try:
                async with session.post(
                    url=url,
                    data=json.dumps(data),
                    headers=self.__headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                    proxy=proxy,
                ) as response:
                    if response.status == HTTPStatus.OK:
                        response_data = await response.json()
                        return response_data
                    if response.status == HTTPStatus.UNAUTHORIZED:
                        raise IncorrectKeyException(
                            'Authorization error. Invalid token.'
                        )
                    if response.status == HTTPStatus.TOO_MANY_REQUESTS:
                        raise ToManyRequestsException(
                            f'To many requests error. URL: {url}'
                        )
                    raise WBApiResponseExceptions(
                        url=url,
                        message=f'Response status-code-{response.status}',
                    )
            except asyncio.TimeoutError:
                raise TimeoutException(
                    'Timeout error. '
                    'WB API did not respond in the allotted time.'
                )

    @staticmethod
    def check_errors(func):
        """Проверить ошибки."""

        @wraps(func)
        async def wrapper(*args, **kwargs) -> Coroutine:
            try:
                start = time()
                response = await func(*args, **kwargs)
                fin = time()
                logger.info(
                    'The response from WB API was received in '
                    f'{round(fin - start, 2)} c.'
                )
                return response
            except IncorrectKeyException as e:
                logger.info(e)
                raise ForUserException(err_mess_templates['error_401'])
            except ToManyRequestsException as e:
                logger.error(e)
                raise ForUserException(err_mess_templates['error_429'])
            except TimeoutException as e:
                logger.error(e)
                raise ForUserException(err_mess_templates['timeout_error'])
            except WBApiResponseExceptions as e:
                logger.error(e)
                raise ForUserException(err_mess_templates['try_later'])

        return wrapper

    @check_errors
    async def get_nm_ids(self):
        """Запрос номенклатур продавца."""
        url = WBApiUrls.GET_NM_IDS
        data = WBApiPayloads.NM_IDS
        response = await self.__get_response_post(url=url, data=data)
        return ResponseHandlers.nm_ids_handler(response)

    @check_errors
    async def get_analytics_detail_days(
        self, nm_ids: list, period: int = 1, aggregation_lvl: str = 'day'
    ) -> dict:
        """Запрос статистики товара по дням."""
        url = WBApiUrls.DETAIL_DAYS
        now_date = datetime.now(tz=MSC_TIME_ZONE).date()
        data = {
            'nmIDs': nm_ids,
            'period': {
                'begin': str(now_date - timedelta(days=period)),
                'end': str(now_date),
            },
            'aggregationLevel': aggregation_lvl,
            'timezone': 'Europe/Moscow',
        }
        response = await self.__get_response_post(url=url, data=data)
        return ResponseHandlers.analytic_detail_days_handler(response)

    @check_errors
    async def get_analytic_detail_periods(self, nm_ids: list, period: int = 7):
        """Запрос статистики товара по периодам."""
        url = WBApiUrls.DETAIL_PERIODS
        now = datetime.utcnow() + MSC_TIME_DELTA
        data = {
            'nmIDs': nm_ids,
            'period': {
                'begin': str(now - timedelta(days=period)),
                'end': str(now),
            },
            'timezone': 'Europe/Moscow',
            'page': 1,
        }
        response = await self.__get_response_post(url=url, data=data)
        return ResponseHandlers.analytic_detail_period_handler(response)
