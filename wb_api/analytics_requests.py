import json
from datetime import datetime, timedelta
from http import HTTPStatus

import aiohttp

from exceptions.wb_exceptions import WBApiResponseExceptions
from .requests_handlers import ResponseHandlers
from .urls_and_payloads import WBApiUrls, WBApiPayloads


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
        Общий метод для получения ответа от WB API.
        :param url:
        :param data:
        :return:
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, data=json.dumps(data), headers=self.__headers) as response:
                if response.status == HTTPStatus.OK:
                    try:
                        response_data = await response.json()
                        return response_data
                    except Exception as e:
                        raise WBApiResponseExceptions(message=e, url=url)
                raise WBApiResponseExceptions(url=url)

    @ResponseHandlers.nm_ids_handler
    async def get_nm_ids(self) -> list[tuple]:
        """
        Получение номенклатур продавца.
        :return: list[tuple]
        """
        url = WBApiUrls.nm_ids_url
        data = WBApiPayloads.nm_ids_payload
        response = await self.__get_response_post(url=url, data=data)
        return response

    @ResponseHandlers.analytic_detail_handler
    async def get_analytics_detail(self,
                                   nm_ids: list,
                                   period: int = 1,
                                   aggregation_lvl: str = 'day') -> list[str, tuple]:
        """
        Получение статистики по переданному номеру номенклатуры.
        :param nm_ids: list
        :param period: int, default: 1
        :param aggregation_lvl: str, default: 'day'
        :return: list[tuple]
        """
        url = WBApiUrls.analytic_detail_url
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
