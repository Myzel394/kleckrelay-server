import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator

from app import constants, life_constants, logger
from app.gpg_handler import gpg
from app.helpers.check_email_is_disposable import check_if_email_is_disposable
from app.helpers.check_email_is_from_relay import check_if_email_is_from_relay
from app.models.enums.alias import ImageProxyFormatType, ProxyUserAgentType
from app.models.user import LanguageType

__all__ = [
    "UserCreate",
    "UserUpdate",
    "User",
    "UserPreferences",
    "SimpleUserResponseModel",
]


class UserBase(BaseModel):
    public_key: Optional[str] = Field(
        max_length=constants.PUBLIC_KEY_MAX_LENGTH,
        default=None,
    )
    encrypted_notes: Optional[str] = Field(
        max_length=constants.ENCRYPTED_NOTES_MAX_LENGTH,
        default=None,
    )
    encrypted_password: Optional[str] = Field(
        max_length=constants.ENCRYPTED_PASSWORD_MAX_LENGTH,
        default=None,
    )
    language: LanguageType = Field(
        default=LanguageType.EN_US
    )

    @validator("public_key")
    def validate_public_key(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        if len(gpg.import_keys(value).fingerprints) == 0:
            raise ValueError(
                "Public key could not be imported."
            )

        return str(value)


# TODO: Add db to this model so that validation happens here
class UserCreate(UserBase):
    email: str = Field(
        regex=constants.EMAIL_REGEX,
        max_length=constants.MAX_EMAIL_LENGTH,
    )


class UserUpdate(UserBase):
    pass


class Email(BaseModel):
    id: uuid.UUID
    address: str
    is_verified: bool

    class Config:
        orm_mode = True


class UserPreferences(BaseModel):
    alias_remove_trackers: bool
    alias_create_mail_report: bool
    alias_proxy_images: bool
    alias_image_proxy_format: ImageProxyFormatType
    alias_proxy_user_agent: ProxyUserAgentType
    alias_expand_url_shorteners: bool

    class Config:
        orm_mode = True


class User(UserBase):
    id: uuid.UUID
    salt: str
    created_at: datetime
    email: Email
    preferences: UserPreferences
    is_admin: bool

    class Config:
        orm_mode = True


class SimpleUserResponseModel(BaseModel):
    user: User
    detail: str
