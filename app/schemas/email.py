from datetime import datetime

from pydantic import BaseModel, Field

from app.constants import MAX_EMAIL_LENGTH

__all__ = [
    "EmailBase",
    "EmailCreate",
    "Email",
]


class EmailBase(BaseModel):
    address: str = Field(
        max_length=MAX_EMAIL_LENGTH,
    )


class EmailCreate(EmailBase):
    pass


class Email(EmailBase):
    id: str
    is_verified: bool
    created_at: datetime

