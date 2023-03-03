from typing import Optional

from pydantic import BaseModel, Field, root_validator

from app import constants

__all__ = [
    "HasUserOTPEnabledResponseModel",
    "UserOTPResponseModel",
    "VerifyOTPModel",
    "DeleteOTPModel",
]


class HasUserOTPEnabledResponseModel(BaseModel):
    enabled: bool


class UserOTPResponseModel(BaseModel):
    secret: str
    recovery_codes: list[str]


class VerifyOTPModel(BaseModel):
    code: str = Field(
        ...,
        regex=constants.OTP_REGEX
    )


class DeleteOTPModel(BaseModel):
    code: Optional[str] = Field(
        None,
        regex=constants.OTP_REGEX,
    )
    recovery_code: Optional[str]

    @root_validator
    def check_code_or_recovery_code(cls, values):
        if not values.get("code") and not values.get("recovery_code"):
            raise ValueError("Must provide either code or recovery_code.")
        return values
