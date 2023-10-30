import json

from pydantic import BaseModel, ValidationError


class BaseResponse(BaseModel):
    """Базовый класс ответа WB API."""
    data: list
    error: bool
    errorText: str
    additionalErrors: None | dict[str, str]


class NmHistoryStatsDays(BaseModel):
    """Статистика по дням. Данные статистики."""
    dt: str
    ordersSumRub: int
    ordersCount: int
    openCardCount: int
    addToCartCount: int
    buyoutsCount: int
    buyoutsSumRub: int
    buyoutPercent: int
    addToCartConversion: int
    cartToOrderConversion: int


class NmDataStatsDays(BaseModel):
    """Статистика по дням. Данные о товаре."""
    nmID: int
    imtName: str
    vendorCode: str
    history: list[NmHistoryStatsDays]


class ResponseStatsDays(BaseResponse):
    """Статистика по дням."""
    data: list[NmDataStatsDays]


class CardsNmIds(BaseModel):
    """Получение артикулов продавца. Данные о товарах."""
    sizes: list[dict]
    mediaFiles: list[str]
    colors: list[str]
    updateAt: str
    vendorCode: str
    brand: str
    object: str
    nmID: int
    imtID: int
    objectID: int
    isProhibited: bool
    tags: list


class DataNmIDs(BaseModel):
    """Получение артикулов продавца."""
    cards: list[CardsNmIds]
    cursor: dict


class ResponseNmIDs(BaseResponse):
    """Получение артикулов продавца."""
    data: DataNmIDs


class PeriodsStatsPeriod(BaseModel):
    """Статистика по периодам. Данные статистики."""
    begin: str
    end: str
    ordersSumRub: int
    ordersCount: int
    openCardCount: int
    addToCartCount: int
    buyoutsCount: int
    buyoutsSumRub: int
    cancelCount: int
    cancelSumRub: int
    avgOrdersCountPerDay: float
    avgPriceRub: int
    conversions: dict[str, int]


class StatisticsStatsPeriod(BaseModel):
    """Статистика по периодам. Выбранный и предыдущий периоды."""
    selectedPeriod: PeriodsStatsPeriod
    previousPeriod: PeriodsStatsPeriod
    periodComparison: dict


class ObjectStatsPeriod(BaseModel):
    """Статистика по периодам. Данные о товаре."""
    id: int
    name: str


class CardsStatsPeriod(BaseModel):
    """Статистика по периодам. Данные о товаре."""
    nmID: int
    vendorCode: str
    brandName: str
    object: ObjectStatsPeriod
    statistics: StatisticsStatsPeriod
    stocks: dict[str, int]


class DataStatsPeriod(BaseModel):
    """Статистика по периодам."""
    page: int
    isNextPage: bool
    cards: list[CardsStatsPeriod]


class ResponseStatsPeriod(BaseResponse):
    """Статистика по периодам."""
    data: DataStatsPeriod


if __name__ == '__main__':

    #  TODO delete after tests
    string_j = """
 
    """

    j_data = json.loads(string_j)
    try:
        d = ResponseStatsPeriod.model_validate(j_data)
    except ValidationError as e:
        print('pydantic_error:', e.json())
    else:
        print(d.data.cards[0].nmID)
