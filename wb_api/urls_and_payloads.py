class WBApiUrls:

    BASE = 'https://suppliers-api.wildberries.ru/'
    GET_NM_IDS = f'{BASE}content/v1/cards/cursor/list'
    DETAIL_DAYS = f'{BASE}content/v1/analytics/nm-report/detail/history'
    DETAIL_PERIODS = f'{BASE}content/v1/analytics/nm-report/detail'


class WBApiPayloads:

    NM_IDS = {
        'sort': {'cursor': {'limit': 100}, 'filter': {'withPhoto': -1}}
    }
    DETAIL_DAYS = {

    }