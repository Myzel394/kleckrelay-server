import uuid

from pydantic import BaseModel, Field

from app.constants import MAX_EMAIL_LENGTH

__all__ = [
    "Email",
]


class EmailBase(BaseModel):
    address: str = Field(
        max_length=MAX_EMAIL_LENGTH,
    )


class Email(EmailBase):
    id: uuid.UUID
    is_verified: bool
