from datetime import datetime

from pydantic import BaseModel, Field

from app.constants import DOMAIN_REGEX, LOCAL_REGEX
from app.life_constants import DOMAIN, MAX_ENCRYPTED_NOTES_SIZE
from user import User

__all__ = [
    "AliasBase",
    "AliasCreate",
    "Alias",
]


class AliasBase(BaseModel):
    is_active: bool
    encrypted_notes: str = Field(
        max_length=MAX_ENCRYPTED_NOTES_SIZE,
    )


class AliasCreate(AliasBase):
    pass


class Alias(AliasBase):
    id: str
    local: str = Field(
        regex=LOCAL_REGEX,
    )
    domain: str = Field(
        regex=DOMAIN_REGEX,
        default=DOMAIN,
    )
    created_at: datetime
    user: User

    class Config:
        orm_mode = True
