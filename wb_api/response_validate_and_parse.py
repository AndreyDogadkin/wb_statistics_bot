import json

from pydantic import BaseModel, ValidationError


class BaseData(BaseModel):
    data: list
    error: bool
    errorText: str
    additionalErrors: None | dict[str, str]


class NmHistoryStatsDays(BaseModel):
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
    nmID: int
    imtName: str
    vendorCode: str
    history: list[NmHistoryStatsDays]


class DataStatsDays(BaseData):
    data: list[NmDataStatsDays]


class CardsNmIds(BaseModel):
    sizes: list[dict[str, int | list]]
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
    cards: list[CardsNmIds]
    cursor: dict


class ResponseNmIDs(BaseData):
    data: DataNmIDs


class PeriodsStatsPeriod(BaseModel):
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
    selectedPeriod: PeriodsStatsPeriod
    previousPeriod: PeriodsStatsPeriod
    periodComparison: dict


class ObjectStatsPeriod(BaseModel):
    id: int
    name: str


class CardsStatsPeriod(BaseModel):
    nmID: int
    vendorCode: str
    brandName: str
    object: ObjectStatsPeriod
    statistics: StatisticsStatsPeriod
    stocks: dict[str, int]


class DataStatsPeriod(BaseModel):
    page: int
    isNextPage: bool
    cards: list[CardsStatsPeriod]


class ResponseStatsPeriod(BaseData):
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
