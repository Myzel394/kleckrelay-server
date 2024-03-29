import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, validator

from app import constants, logger
from app.gpg_handler import gpg
from app.schemas.global_settings import GlobalSettingsModel
from app.utils.check_email_is_disposable import check_if_email_is_disposable
from app.utils.check_email_is_from_relay import check_if_email_is_from_relay
from app.models.enums.alias import ImageProxyFormatType, ProxyUserAgentType
from app.models.user import LanguageType

__all__ = [
    "UserCreate",
    "UserUpdate",
    "UserDetail",
    "UserDetailWithoutPreferences",
    "UserPreferences",
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


class UserCreate(UserBase):
    settings: GlobalSettingsModel
    email: str = Field(
        regex=constants.EMAIL_REGEX,
        max_length=constants.MAX_EMAIL_LENGTH,
    )

    @validator("email")
    def validate_email(cls, value: str, values: dict[str, Any]) -> str:
        settings: GlobalSettingsModel = values["settings"]
        if not settings.user_email_enable_other_relays and check_if_email_is_from_relay(value):
            logger.info("Request: Signup -> Email is from another relay.")
            raise ValueError(
                "Email is from another relay. "
                "This instance does not allow using another email relay."
            )

        if not settings.user_email_enable_disposable_emails and check_if_email_is_disposable(value):
            logger.info("Request: Signup -> Email is disposable.")
            raise ValueError(
                "Email is disposable. This instance does not allow using disposable emails.",
            )
        return value


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
    alias_reject_on_privacy_leak: bool

    class Config:
        orm_mode = True


class UserDetailWithoutPreferences(UserBase):
    id: uuid.UUID
    salt: str
    created_at: datetime
    email: Email
    is_admin: bool

    class Config:
        orm_mode = True


class UserDetail(UserDetailWithoutPreferences):
    preferences: UserPreferences

    class Config:
        orm_mode = True


