from datetime import datetime

from pydantic import BaseModel, Field

__all__ = [
    "UserBase",
    "UserCreate",
    "User",
]


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    public_key: str
    encrypted_private_key: str


class User(UserBase):
    id: str
    created_at: datetime
    encrypted_private_key: str
    public_key: str

    class Config:
        orm_mode = True
