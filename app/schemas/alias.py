from pydantic import BaseModel

from user import User

__all__ = [
    "AliasBase",
    "AliasCreate",
    "Alias",
]


class AliasBase(BaseModel):
    local: str
    domain: str
    is_active: bool
    encrypted_notes: str


class AliasCreate(AliasBase):
    pass


class Alias(AliasBase):
    user: User

    class Config:
        orm_mode = True
