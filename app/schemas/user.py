import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, root_validator

from app import constants

__all__ = [
    "UserCreate",
    "User",
]


class UserBase(BaseModel):
    public_key: Optional[str] = Field(
        regex=constants.PUBLIC_KEY_REGEX,
        max_length=constants.PUBLIC_KEY_MAX_LENGTH,
        default=None,
    )
    encrypted_private_key: Optional[str] = Field(
        max_length=constants.ENCRYPTED_PRIVATE_KEY_MAX_LENGTH,
        defualt=None,
    )


class UserCreate(UserBase):
    email: str = Field(
        regex=constants.EMAIL_REGEX,
        max_length=constants.MAX_EMAIL_LENGTH,
    )
    password: Optional[str]

    @root_validator()
    def validate_public_key(cls, values: dict) -> dict:
        if "password" and "encrypted_private_key" not in values:
            raise ValueError(
                "If a `password` is set, the `encrypted_private_key` must also be set."
            )

        return values


class Email(BaseModel):
    id: uuid.UUID
    address: str
    is_verified: bool

    class Config:
        orm_mode = True


class User(UserBase):
    id: uuid.UUID
    created_at: datetime
    email: Email

    class Config:
        orm_mode = True
