from pydantic import BaseModel

__all__ = [
    "HasUserOTPEnabledResponseModel",
    "UserOTPResponseModel"
]


class HasUserOTPEnabledResponseModel(BaseModel):
    enabled: bool


class UserOTPResponseModel(BaseModel):
    id: str
    secret: str
    uri: str
