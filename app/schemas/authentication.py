from typing import Optional

from pydantic import BaseModel, Field

from app.constants import EMAIL_LOGIN_TOKEN_SAME_REQUEST_TOKEN_LENGTH, EMAIL_REGEX, MAX_EMAIL_LENGTH
from app.life_constants import EMAIL_LOGIN_TOKEN_LENGTH
from app.models import User

__all__ = [
    "EmailLoginTokenResponseModel",
    "EmailLoginTokenVerifyModel",
    "VerifyEmailModel",
    "LoginWithEmailTokenModel",
    "User",
    "SignupResponseModel",
    "ResendEmailModel",
    "EmailLoginTokenChangeModel",
    "EmailLoginTokenChangeAllowFromDifferentDevicesModel",
    "ResendEmailAlreadyVerifiedResponseModel",
]


class EmailLoginTokenResponseModel(BaseModel):
    same_request_token: str
    detail: str


class EmailLoginTokenChangeModel(BaseModel):
    email: str = Field(
        regex=EMAIL_REGEX,
        max_length=MAX_EMAIL_LENGTH,
    )
    same_request_token: str = Field(
        max_length=EMAIL_LOGIN_TOKEN_SAME_REQUEST_TOKEN_LENGTH,
    )


class EmailLoginTokenChangeAllowFromDifferentDevicesModel(BaseModel):
    allow: bool


class EmailLoginTokenVerifyModel(BaseModel):
    email: str = Field(
        regex=EMAIL_REGEX,
        max_length=MAX_EMAIL_LENGTH,
    )
    token: str = Field(
        max_length=EMAIL_LOGIN_TOKEN_LENGTH,
    )
    same_request_token: Optional[str] = Field(
        max_length=EMAIL_LOGIN_TOKEN_SAME_REQUEST_TOKEN_LENGTH,
    )


class ResendEmailModel(BaseModel):
    email: str


class VerifyEmailModel(BaseModel):
    email: str
    token: str


class LoginWithEmailTokenModel(BaseModel):
    email: str


class SignupResponseModel(BaseModel):
    normalized_email: str
    detail: str


class ResendEmailAlreadyVerifiedResponseModel(BaseModel):
    detail: str
    code: str = "ok:email_already_verified"

