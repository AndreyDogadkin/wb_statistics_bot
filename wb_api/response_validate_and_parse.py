from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """Базовый класс ответа WB API."""
    data: list
    error: bool
    error_text: str = Field(alias='errorText')
    additional_errors: None | dict[str, str] = Field(alias='additionalErrors')


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


class NmDataStatsDays(BaseModel):
    """Статистика по дням. Данные о товаре."""
    nm_id: int = Field(alias='nmID')
    imt_name: str = Field(alias='imtName')
    vendor_code: str = Field(alias='vendorCode')
    history: list[NmHistoryStatsDays]


class ResponseStatsDays(BaseResponse):
    """Статистика по дням."""
    data: list[NmDataStatsDays]


class CardsNmIds(BaseModel):
    """Получение артикулов продавца. Данные о товарах."""
    sizes: list[dict]
    media_files: list[str] = Field(alias='mediaFiles')
    colors: list[str]
    update_at: str = Field(alias='updateAt')
    vendor_code: str = Field(alias='vendorCode')
    brand: str
    object: str
    nm_id: int = Field(alias='nmID')
    imt_id: int = Field(alias='imtID')
    object_id: int = Field(alias='objectID')
    is_prohibited: bool = Field(alias='isProhibited')
    tags: list


class DataNmIDs(BaseModel):
    """Получение артикулов продавца."""
    cards: list[CardsNmIds]
    cursor: dict


class ResponseNmIDs(BaseResponse):
    """Получение артикулов продавца."""
    data: DataNmIDs


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
    conversions: ConversionsStatsPeriod


class StatisticsStatsPeriod(BaseModel):
    """Статистика по периодам. Выбранный и предыдущий периоды."""
    selected_period: PeriodsStatsPeriod = Field(alias='selectedPeriod')
    previous_period: PeriodsStatsPeriod = Field(alias='previousPeriod')
    period_comparison: dict = Field(alias='periodComparison')


class ObjectStatsPeriod(BaseModel):
    """Статистика по периодам. Данные о товаре."""
    id: int
    name: str


class CardsStatsPeriod(BaseModel):
    """Статистика по периодам. Данные о товаре."""
    nm_id: int = Field(alias='nmID')
    vendor_code: str = Field(alias='vendorCode')
    brand_name: str = Field(alias='brandName')
    object: ObjectStatsPeriod
    statistics: StatisticsStatsPeriod
    stocks: dict[str, int]


class DataStatsPeriod(BaseModel):
    """Статистика по периодам."""
    page: int
    is_next_page: bool = Field(alias='isNextPage')
    cards: list[CardsStatsPeriod]


class ResponseStatsPeriod(BaseResponse):
    """Статистика по периодам."""
    data: DataStatsPeriod
