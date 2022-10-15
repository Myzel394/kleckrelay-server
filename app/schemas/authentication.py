import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.constants import EMAIL_LOGIN_TOKEN_SAME_REQUEST_TOKEN_LENGTH, EMAIL_REGEX, MAX_EMAIL_LENGTH
from app.life_constants import EMAIL_LOGIN_TOKEN_LENGTH
from app.models.enums.alias import ImageProxyFormatType, ProxyUserAgentType

__all__ = [
    "EmailLoginTokenResponseModel",
    "EmailLoginTokenVerifyModel",
    "AuthenticationCredentialsResponseModel",
    "VerifyEmailModel",
    "LoginWithEmailTokenModel",
    "User",
    "SignupResponseModel",
    "ResendEmailModel",
]


class UserPreferences(BaseModel):
    alias_remove_trackers: bool
    alias_create_mail_report: bool
    alias_proxy_images: bool
    alias_image_proxy_format: ImageProxyFormatType
    alias_image_proxy_user_agent: ProxyUserAgentType

    class Config:
        orm_mode = True


class Email(BaseModel):
    address: str
    is_verified: bool

    class Config:
        orm_mode = True


class User(BaseModel):
    id: uuid.UUID
    created_at: datetime
    email: Email
    preferences: UserPreferences

    class Config:
        orm_mode = True


class EmailLoginTokenResponseModel(BaseModel):
    same_request_token: str
    detail: str


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
    user: User
    detail: str


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

