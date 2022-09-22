import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from app.constants import (
    EMAIL_REGEX, ENCRYPTED_PASSWORD_LENGTH, MAX_EMAIL_LENGTH,
)

__all__ = [
    "UserCreate",
    "User",
]


class UserBase(BaseModel):
    encrypted_password: str = Field(
        max_length=ENCRYPTED_PASSWORD_LENGTH,
    )


class UserCreate(UserBase):
    email: str = Field(
        regex=EMAIL_REGEX,
        max_length=MAX_EMAIL_LENGTH,
    )


class Email(BaseModel):
    id: uuid.UUID
    address: str
    verified_at: Optional[datetime]
    created_at: datetime

    class Config:
        orm_mode = True


class User(UserBase):
    id: uuid.UUID
    created_at: datetime
    email: Email

    class Config:
        orm_mode = True
