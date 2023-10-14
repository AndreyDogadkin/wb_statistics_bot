import json

from pydantic import BaseModel, ValidationError


class NmHistory(BaseModel):
    dt: str
    openCardCount: int
    addToCartCount: int
    addToCartConversion: int
    ordersCount: int
    ordersSumRub: int
    cartToOrderConversion: int
    buyoutsCount: int
    buyoutsSumRub: int
    buyoutPercent: int


class NmData(BaseModel):
    nmID: int
    imtName: str
    vendorCode: str
    history: list[NmHistory]


class DataAnalyticDays(BaseModel):
    data: list[NmData]
    error: bool
    errorText: str
    additionalErrors: None | dict[str, str]


if __name__ == '__main__':

    #  TODO delete after tests
    string_j = """
    {
        "data": [
            {
                "nmID": 162935859,
                "imtName": "Рогатка спортивная рыболовная",
                "vendorCode": "slingshot",
                "history": [
                    {
                        "dt": "2023-09-27",
                        "openCardCount": 109,
                        "addToCartCount": 15,
                        "addToCartConversion": 14,
                        "ordersCount": 2,
                        "ordersSumRub": 1000,
                        "cartToOrderConversion": 13,
                        "buyoutsCount": 2,
                        "buyoutsSumRub": 1000,
                        "buyoutPercent": 100
                    },
                    {
                        "dt": "2023-09-28",
                        "openCardCount": 125,
                        "addToCartCount": 21,
                        "addToCartConversion": 17,
                        "ordersCount": 3,
                        "ordersSumRub": 1500,
                        "cartToOrderConversion": 14,
                        "buyoutsCount": 3,
                        "buyoutsSumRub": 1500,
                        "buyoutPercent": 100
                    }
                ]
            }
        ],
        "error": false,
        "errorText": "",
        "additionalErrors": null
    }
    """

    j_data = json.loads(string_j)
    try:
        d = DataAnalyticDays.model_validate(j_data)
    except ValidationError as e:
        print('pydantic_error:', e.json())
    else:
        print(d.data[0].imtName)
