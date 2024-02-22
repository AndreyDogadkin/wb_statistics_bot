from bot.base.messages_templates import get_stats_mess_templates
from bot.services.wb_api.analytics_requests import StatisticsRequests


async def get_user_statistics(
    statistics: StatisticsRequests, nm_id: int, period: int
) -> tuple[str, str]:
    """Получить и обработать статистику пользователя."""
    message_template = get_stats_mess_templates[
        'send_analytic_detail_days_mess_template'
    ]
    get_stats_func = statistics.get_analytics_detail_days
    if period > 5:
        message_template = get_stats_mess_templates[
            'send_analytic_detail_period_mess_template'
        ]
        get_stats_func = statistics.get_analytic_detail_periods
    statistics_nm_id: list = await get_stats_func(
        nm_ids=[nm_id], period=period
    )
    if statistics_nm_id:
        product: tuple[str, str] = statistics_nm_id.pop(0)
        answer_message: str = get_stats_mess_templates[
            'product_vendor_code'
        ].format(*product)
        for nm in statistics_nm_id:
            answer_message += message_template.format(*nm)
        return product[1], answer_message
