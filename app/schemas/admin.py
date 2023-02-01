import uuid

from pydantic import BaseModel

__all__ = [
    "AdminUsersResponseModel"
]


class AdminUsersResponseUserEmailModel(BaseModel):
    id: uuid.UUID
    address: str

    class Config:
        orm_mode = True


class AdminUsersResponseUserModel(BaseModel):
    id: uuid.UUID
    email: AdminUsersResponseUserEmailModel

    class Config:
        orm_mode = True


class AdminUsersResponseModel(BaseModel):
    users: list[AdminUsersResponseUserModel]
