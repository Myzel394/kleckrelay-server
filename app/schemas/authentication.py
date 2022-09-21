from pydantic import BaseModel, Field

from app.constants import EMAIL_REGEX, MAX_EMAIL_LENGTH, EMAIL_LOGIN_TOKEN_SAME_REQUEST_TOKEN_LENGTH
from app.life_constants import EMAIL_LOGIN_TOKEN_LENGTH
from app.schemas.user import User

__all__ = [
    "AuthenticationCredentialsResponseModel",
    "EmailLoginTokenResponseModel",
    "EmailLoginTokenVerifyModel",
]


class AuthenticationCredentialsResponseModel(BaseModel):
    user: User
    access_token: str
    refresh_token: str


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
