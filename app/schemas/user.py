from datetime import datetime

from pydantic import BaseModel, Field
from app.constants import EMAIL_REGEX, MAX_EMAIL_LENGTH, PRIVATE_KEY_REGEX, PUBLIC_KEY_REGEX
from email import Email

__all__ = [
    "UserBase",
    "UserCreate",
    "User",
]


class UserBase(BaseModel):
    public_key: str = Field(
        regex=PUBLIC_KEY_REGEX,
    )
    encrypted_private_key: str = Field(
        regex=PRIVATE_KEY_REGEX,
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
