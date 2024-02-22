from pydantic import BaseModel, Field

from bot.services.wb_api.schemas.base import BaseResponse


class ResponseStatsPeriod(BaseResponse):
    """Статистика по периодам."""

    data: 'DataStatsPeriod'


class DataStatsPeriod(BaseModel):
    """Статистика по периодам."""

    page: int
    is_next_page: bool = Field(alias='isNextPage')
    cards: list['CardsStatsPeriod']


class CardsStatsPeriod(BaseModel):
    """Статистика по периодам. Данные о товаре."""

    nm_id: int = Field(alias='nmID')
    vendor_code: str = Field(alias='vendorCode')
    brand_name: str = Field(alias='brandName')
    object: 'ObjectStatsPeriod'
    statistics: 'StatisticsStatsPeriod'
    stocks: dict[str, int]


class ObjectStatsPeriod(BaseModel):
    """Статистика по периодам. Данные о товаре."""

    id: int
    name: str


class StatisticsStatsPeriod(BaseModel):
    """Статистика по периодам. Выбранный и предыдущий периоды."""

    selected_period: 'PeriodsStatsPeriod' = Field(alias='selectedPeriod')
    previous_period: 'PeriodsStatsPeriod' = Field(alias='previousPeriod')
    period_comparison: dict = Field(alias='periodComparison')


class ConversionsStatsPeriod(BaseModel):
    """Статистика по периодам. Конверсия."""

    add_to_cart_percent: int = Field(alias='addToCartPercent')
    cart_to_order_percent: int = Field(alias='cartToOrderPercent')
    buyout_percent: int = Field(alias='buyoutsPercent')


class PeriodsStatsPeriod(BaseModel):
    """Статистика по периодам. Данные статистики."""

    begin: str
    end: str
    orders_sum_rub: int = Field(alias='ordersSumRub')
    orders_count: int = Field(alias='ordersCount')
    open_card_count: int = Field(alias='openCardCount')
    add_to_cart_count: int = Field(alias='addToCartCount')
    buyouts_count: int = Field(alias='buyoutsCount')
    buyouts_sum_rub: int = Field(alias='buyoutsSumRub')
    cancel_count: int = Field(alias='cancelCount')
    cancel_sum_rub: int = Field(alias='cancelSumRub')
    avg_orders_count_per_day: float = Field(alias='avgOrdersCountPerDay')
    avg_price_rub: int = Field(alias='avgPriceRub')
    conversions: 'ConversionsStatsPeriod'
