class WBApiUrls:
    BASE = 'https://seller-analytics-api.wildberries.ru/api/v2/'
    GET_NM_IDS = (
        'https://suppliers-api.wildberries.ru/content/v2/get/cards/list'
    )
    DETAIL_DAYS = f'{BASE}nm-report/detail/history'
    DETAIL_PERIODS = f'{BASE}nm-report/detail'


class WBApiPayloads:
    NM_IDS = {
        'settings': {'cursor': {'limit': 100}, 'filter': {'withPhoto': -1}}
    }
