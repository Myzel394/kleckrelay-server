import uuid

from pydantic import BaseModel

__all__ = [
    "HasUserOTPEnabledResponseModel",
    "UserOTPResponseModel",
    "VerifyOTPModel",
]


class HasUserOTPEnabledResponseModel(BaseModel):
    enabled: bool


class UserOTPResponseModel(BaseModel):
    secret: str


class VerifyOTPModel(BaseModel):
    code: str
