from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """Базовый класс ответа WB API."""
    data: list
    error: bool
    error_text: str = Field(alias='errorText')
    additional_errors: None | dict[str, str] = Field(alias='additionalErrors')
