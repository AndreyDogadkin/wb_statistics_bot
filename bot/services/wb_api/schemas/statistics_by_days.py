from pydantic import BaseModel, Field

from bot.services.wb_api.schemas.base import BaseResponse


class ResponseStatsDays(BaseResponse):
    """Статистика по дням."""

    data: list['NmDataStatsDays']


class NmDataStatsDays(BaseModel):
    """Статистика по дням. Данные о товаре."""

    nm_id: int = Field(alias='nmID')
    imt_name: str = Field(alias='imtName')
    vendor_code: str = Field(alias='vendorCode')
    history: list['NmHistoryStatsDays']


class NmHistoryStatsDays(BaseModel):
    """Статистика по дням. Данные статистики."""

    dt: str
    orders_sum_rub: int = Field(alias='ordersSumRub')
    orders_count: int = Field(alias='ordersCount')
    open_card_count: int = Field(alias='openCardCount')
    add_to_cart_count: int = Field(alias='addToCartCount')
    buyouts_count: int = Field(alias='buyoutsCount')
    buyouts_sum_rub: int = Field(alias='buyoutsSumRub')
    buyout_percent: int = Field(alias='buyoutPercent')
    add_to_cart_conversion: int = Field(alias='addToCartConversion')
    cart_to_order_conversion: int = Field(alias='cartToOrderConversion')
