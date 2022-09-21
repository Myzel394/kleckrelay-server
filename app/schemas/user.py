from datetime import datetime

from pydantic import BaseModel, Field
from app.constants import (
    EMAIL_REGEX, ENCRYPTED_PASSWORD_LENGTH, MAX_EMAIL_LENGTH,
)
from email import Email

__all__ = [
    "UserBase",
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


class User(UserBase):
    id: str
    created_at: datetime
    email: Email

    class Config:
        orm_mode = True
