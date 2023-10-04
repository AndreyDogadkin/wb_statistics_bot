from dataclasses import dataclass


@dataclass
class WBApiUrls:
    nm_ids_url = 'https://suppliers-api.wildberries.ru/content/v1/cards/cursor/list'
    analytic_detail_url = 'https://suppliers-api.wildberries.ru/content/v1/analytics/nm-report/detail/history'


@dataclass
class WBApiPayloads:
    nm_ids_payload = {
        "sort": {
            "cursor": {
                "limit": 50
            },
            "filter": {
                "withPhoto": -1
            }
        }
    }
