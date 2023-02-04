from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, root_validator, validator

from app.constants import LOCAL_REGEX, MAX_LOCAL_LENGTH

__all__ = [
    "ReservedAliasCreate",
    "ReservedAliasUpdate",
    "ReservedAliasDetail",
]

# Utils


class ReservedAliasUserEmail(BaseModel):
    id: UUID
    address: str

    class Config:
        orm_mode = True


class ReservedAliasUser(BaseModel):
    id: UUID
    email: ReservedAliasUserEmail

    class Config:
        orm_mode = True


class ReservedAliasCreateUser(BaseModel):
    id: UUID


class ReservedAliasUserEmailDetail(BaseModel):
    id: UUID
    address: str


class ReservedAliasUserDetail(BaseModel):
    id: UUID
    email: ReservedAliasUserEmailDetail


# ReservedAlias

class ReservedAliasBase(BaseModel):
    is_active: Optional[bool]


class ReservedAliasCreate(ReservedAliasBase):
    local: str = Field(
        regex=LOCAL_REGEX,
        default=None,
        max_length=MAX_LOCAL_LENGTH,
        description="Only required if type == AliasType.CUSTOM. To avoid collisions, a random "
                    "suffix will be added to the end.",
    )
    users: list[ReservedAliasCreateUser]

    @validator("users")
    def check_users(cls, value: list[ReservedAliasCreateUser]) -> list[ReservedAliasCreateUser]:
        if len(value) < 1:
            raise ValueError("At least one user must be provided.")

        return value

    class Config:
        orm_mode = True


class ReservedAliasUpdate(ReservedAliasBase):
    users: Optional[list[ReservedAliasCreateUser]]

    @validator("users")
    def check_users(cls, value: list[ReservedAliasCreateUser]) -> list[ReservedAliasCreateUser]:
        if len(value) < 1:
            raise ValueError("At least one user must be provided.")

        return value

    class Config:
        orm_mode = True


class ReservedAliasDetail(ReservedAliasBase):
    id: UUID
    local: str
    domain: str
    users: list[ReservedAliasUser]

    class Config:
        orm_mode = True
