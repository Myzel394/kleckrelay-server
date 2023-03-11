import uuid
from datetime import date, timedelta

from pydantic import BaseModel, Field, validator

from app import constants, life_constants
from app.models.enums.api_key import APIKeyScope

__all__ = [
    "APIKeyCreateModel",
    "APIKeyCreatedResponseModel",
    "APIKeyDeleteModel",
    "APIKeyResponseModel",
]


class APIKeyCreateModel(BaseModel):
    expires_at: date = Field(
        default_factory=lambda: date.today() + constants.DEFAULT_API_EXPIRE_DURATION
    )
    scopes: list[APIKeyScope]
    label: str = Field(
        ...,
        max_length=constants.API_KEY_MAX_LABEL_LENGTH,
    )

    @validator("expires_at")
    def validate_expires_at(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("Expiration date must be in the future.")

        if value > date.today() + timedelta(days=life_constants.API_KEY_MAX_DAYS):
            raise ValueError("Expiration date can't be that far in the future.")

        return value

    @validator("scopes")
    def validate_scopes(cls, value: list[APIKeyScope]) -> list[APIKeyScope]:
        if len(value) == 0:
            raise ValueError("You must provide at least one scope.")

        return value


class APIKeyResponseModel(BaseModel):
    id: uuid.UUID
    expires_at: date
    scopes: list[APIKeyScope]
    label: str

    class Config:
        orm_mode = True


class APIKeyCreatedResponseModel(APIKeyResponseModel):
    key: str


class APIKeyDeleteModel(BaseModel):
    key: str = Field(
        ...,
        min_length=life_constants.API_KEY_LENGTH,
        max_length=life_constants.API_KEY_LENGTH,
    )
