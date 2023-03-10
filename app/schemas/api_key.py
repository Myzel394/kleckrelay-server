import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app import constants
from app.models.enums.api_key import APIKeyScope

__all__ = [
    "APIKeyCreateModel",
    "APIKeyCreatedResponseModel",
]


class APIKeyCreateModel(BaseModel):
    expires_at: datetime = Field(
        default_factory=lambda: datetime.utcnow() + constants.DEFAULT_API_EXPIRE_DURATION
    )
    scopes: list[APIKeyScope]
    label: str = Field(
        ...,
        max_length=constants.API_KEY_MAX_LABEL_LENGTH,
    )


class APIKeyModel(BaseModel):
    id: uuid.UUID
    expires_at: datetime
    scopes: list[APIKeyScope]
    label: str


class APIKeyCreatedResponseModel(APIKeyModel):
    key: str
