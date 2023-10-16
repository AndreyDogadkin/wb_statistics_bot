import json
from datetime import datetime, timedelta
from http import HTTPStatus

import aiohttp

from exceptions.wb_exceptions import WBApiResponseExceptions
from .response_handlers import ResponseHandlers
from .urls_and_payloads import wb_api_urls, wb_api_payloads


class StatisticsRequests:

    def __init__(self, wb_token):
        self.token = wb_token
        self.__headers = {'Authorization': self.token,
                          'Content-type': 'application/json',
                          'Accept': 'text/plain',
                          'Content-Encoding': 'utf-8',
                          }

    async def __get_response_post(self, url, data):
        """
        Сессия для получения ответа от WB API.
        :param url:
        :param data:
        :return:
        """
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:  # TODO разобраться с таймаутом и отловом ошибки таймаута
            async with session.post(url=url, data=json.dumps(data), headers=self.__headers) as response:
                if response.status == HTTPStatus.OK:
                    try:
                        response_data = await response.json()
                        return response_data
                    except Exception as e:
                        raise WBApiResponseExceptions(message=e, url=url)
                raise WBApiResponseExceptions(url=url, message=response.status)

    @ResponseHandlers.nm_ids_handler
    async def get_nm_ids(self) -> list[tuple]:
        """
        Получение номенклатур продавца.
        :return: list[tuple]
        """
        url = wb_api_urls['get_nm_ids_url']
        data = wb_api_payloads['nm_ids_payload']
        response = await self.__get_response_post(url=url, data=data)
        return response

    @ResponseHandlers.analytic_detail_days_handler
    async def get_analytics_detail_days(self,
                                        nm_ids: list,
                                        period: int = 1,
                                        aggregation_lvl: str = 'day') -> list[str, tuple]:
        """
        Получение статистики по переданному номеру номенклатуры.
        :param nm_ids: list
        :param period: int
        :param aggregation_lvl
        :return: list[tuple]
        """
        url = wb_api_urls['analytic_detail_url_days']
        data = {
            'nmIDs': nm_ids,
            'period': {
                'begin': str(datetime.now().date() - timedelta(days=period)),
                'end': str(datetime.now().date())
            },
            'aggregationLevel': aggregation_lvl
        }
        response = await self.__get_response_post(url=url, data=data)
        return response

    @ResponseHandlers.analytic_detail_period_handler
    async def get_analytic_detail_periods(self, nm_ids: list, period: int = 7):
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
        return response

    # TODO добавить просмотр остатков товаров (В документации -> статистика -> склад)
    # TODO добавить продажи (в документации -> статистика -> продажи)
