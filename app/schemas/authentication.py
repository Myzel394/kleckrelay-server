import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.constants import EMAIL_REGEX, MAX_EMAIL_LENGTH, EMAIL_LOGIN_TOKEN_SAME_REQUEST_TOKEN_LENGTH
from app.life_constants import EMAIL_LOGIN_TOKEN_LENGTH

__all__ = [
    "EmailLoginTokenResponseModel",
    "EmailLoginTokenVerifyModel",
    "LoginWithEmailTokenModel",
    "User",
]


class Email(BaseModel):
    id: uuid.UUID
    address: str
    is_verified: bool

    class Config:
        orm_mode = True


class User(BaseModel):
    id: uuid.UUID
    created_at: datetime
    email: Email

    class Config:
        orm_mode = True


class EmailLoginTokenResponseModel(BaseModel):
    same_request_token: str


class EmailLoginTokenVerifyModel(BaseModel):
    email: str = Field(
        regex=EMAIL_REGEX,
        max_length=MAX_EMAIL_LENGTH,
    )
    token: str = Field(
        max_length=EMAIL_LOGIN_TOKEN_LENGTH,
    )
    same_request_token: str = Field(
        max_length=EMAIL_LOGIN_TOKEN_SAME_REQUEST_TOKEN_LENGTH,
    )


class AuthenticationCredentialsResponseModel(BaseModel):
    access_token: str
    refresh_token: str


class VerifyEmailModel(BaseModel):
    email: str
    token: str


class LoginWithEmailTokenModel(BaseModel):
    email: str

