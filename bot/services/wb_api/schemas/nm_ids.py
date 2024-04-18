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

    nm_id: int = Field(alias='nmID')
    nm_uuid: str = Field(alias='nmUUID')
    object_id: int = Field(alias='subjectID')
    vendor_code: str = Field(alias='vendorCode')
    brand: str
    title: str
    description: str
    video: str | None = None
    media_files: list[dict] = Field(alias='photos')
    dimensions: dict
    characteristics: list[dict]
    created_at: str = Field(alias='createdAt')
    update_at: str = Field(alias='updatedAt')
    imt_id: int = Field(alias='imtID')
    sizes: list[dict]
    subject_name: str = Field(alias='subjectName')
