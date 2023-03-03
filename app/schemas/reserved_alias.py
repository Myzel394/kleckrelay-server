from typing import Optional
import uuid

from pydantic import BaseModel, Field, validator

from app.constants import LOCAL_REGEX, MAX_LOCAL_LENGTH

__all__ = [
    "ReservedAliasCreate",
    "ReservedAliasUpdate",
    "ReservedAliasDetail",
]

from app.utils.email import is_local_a_bounce_address


# Utils


class ReservedAliasUserEmail(BaseModel):
    id: uuid.UUID
    address: str

    class Config:
        orm_mode = True


class ReservedAliasUser(BaseModel):
    id: uuid.UUID
    email: ReservedAliasUserEmail

    class Config:
        orm_mode = True


class ReservedAliasCreateUser(BaseModel):
    id: uuid.UUID


class ReservedAliasUserEmailDetail(BaseModel):
    id: uuid.UUID
    address: str


class ReservedAliasUserDetail(BaseModel):
    id: uuid.UUID
    email: ReservedAliasUserEmailDetail


# ReservedAlias

class ReservedAliasBase(BaseModel):
    is_active: Optional[bool]


class ReservedAliasCreate(ReservedAliasBase):
    local: str = Field(
        regex=LOCAL_REGEX,
        default=None,
        max_length=MAX_LOCAL_LENGTH,
    )
    users: list[ReservedAliasCreateUser]

    @validator("local")
    def check_local_is_not_a_forbidden_name(cls, value: str) -> str:
        if is_local_a_bounce_address(value):
            raise ValueError(f"This address cannot be used as it is required by the system.")

        return value

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
    id: uuid.UUID
    local: str
    domain: str
    users: list[ReservedAliasUser]

    class Config:
        orm_mode = True
