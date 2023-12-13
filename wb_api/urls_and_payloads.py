wb_api_urls: dict = {
    'get_nm_ids_url':
        'https://suppliers-api.wildberries.ru/content/v1/cards/cursor/list',
    'analytic_detail_url_days':
        'https://suppliers-api.wildberries.ru/content/v1/analytics/nm-report/detail/history',
    'analytic_detail_url_periods':
        'https://suppliers-api.wildberries.ru/content/v1/analytics/nm-report/detail',
}

wb_api_payloads: dict = {
    'nm_ids_payload': {'sort': {'cursor': {'limit': 50}, 'filter': {'withPhoto': -1}}},
}
