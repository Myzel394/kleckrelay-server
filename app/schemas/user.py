from datetime import datetime

from pydantic import BaseModel, Field
from app.constants import EMAIL_REGEX, MAX_EMAIL_LENGTH, PRIVATE_KEY_REGEX, PUBLIC_KEY_REGEX

__all__ = [
    "UserBase",
    "UserCreate",
    "User",
]


class UserBase(BaseModel):
    email: str = Field(
        regex=EMAIL_REGEX,
        max_length=MAX_EMAIL_LENGTH,
    )


class UserCreate(UserBase):
    public_key: str = Field(
        regex=PUBLIC_KEY_REGEX,
    )
    encrypted_private_key: str = Field(
        regex=PRIVATE_KEY_REGEX,
    )


class User(UserBase):
    id: str
    created_at: datetime
    encrypted_private_key: str
    public_key: str

    class Config:
        orm_mode = True
