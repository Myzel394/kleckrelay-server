import uuid
from datetime import datetime

from pydantic import BaseModel, Field
from app.constants import (
    EMAIL_REGEX, MAX_EMAIL_LENGTH,
)

__all__ = [
    "UserCreate",
    "User",
]


class UserBase(BaseModel):
    pass


class UserCreate(UserBase):
    email: str = Field(
        regex=EMAIL_REGEX,
        max_length=MAX_EMAIL_LENGTH,
    )


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
