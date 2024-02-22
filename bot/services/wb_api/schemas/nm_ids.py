from pydantic import BaseModel, Field

from bot.services.wb_api.schemas.base import BaseResponse


class ResponseNmIDs(BaseResponse):
    """Получение артикулов продавца."""

    data: 'DataNmIDs'


class DataNmIDs(BaseModel):
    """Получение артикулов продавца."""

    cards: list['CardsNmIds']
    cursor: dict


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
