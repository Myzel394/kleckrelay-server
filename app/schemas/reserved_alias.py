from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, root_validator

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
    users: list[ReservedAliasUser]

    @root_validator()
    def check_users(cls, values) -> dict[str, Any]:
        if not values.get("users"):
            raise ValueError("`users` must be provided.")

        if len(values["users"]) < 1:
            raise ValueError("`users` must contain at least one user.")

        return values

    class Config:
        orm_mode = True


class ReservedAliasUpdate(ReservedAliasBase):
    users: Optional[list[ReservedAliasUser]]

    @root_validator()
    def check_users(cls, values) -> dict[str, Any]:
        if (users := values.get("users")) is not None:
            if len(users) < 1:
                raise ValueError("`users` must contain at least one user.")

        return values

    class Config:
        orm_mode = True


class ReservedAliasDetail(ReservedAliasBase):
    id: UUID
    local: str
    domain: str
    users: list[ReservedAliasUser]

    class Config:
        orm_mode = True
