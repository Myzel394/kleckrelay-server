import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, root_validator, validator

from app import constants, life_constants, logger
from app.helpers.check_email_is_disposable import check_if_email_is_disposable
from app.helpers.check_email_is_from_relay import check_if_email_is_from_relay
from app.models import User
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
        regex=constants.PUBLIC_KEY_REGEX,
        max_length=constants.PUBLIC_KEY_MAX_LENGTH,
        default=None,
    )
    encrypted_private_key: Optional[str] = Field(
        max_length=constants.ENCRYPTED_PRIVATE_KEY_MAX_LENGTH,
        defualt=None,
    )
    language: LanguageType = Field(
        default=LanguageType.EN_US
    )


class UserCreate(UserBase):
    email: str = Field(
        regex=constants.EMAIL_REGEX,
        max_length=constants.MAX_EMAIL_LENGTH,
    )
    password: Optional[str]

    @root_validator()
    def validate_public_key(cls, values: dict) -> dict:
        if "password" and "encrypted_private_key" not in values:
            raise ValueError(
                "If a `password` is set, the `encrypted_private_key` must also be set."
            )

        return values

    @validator("email")
    def validate_email(cls, value: str) -> str:
        if not life_constants.USER_EMAIL_ENABLE_OTHER_RELAYS \
                and check_if_email_is_from_relay(value):
            logger.info("Request: Signup -> Email is from another relay.")
            raise ValueError(
                "Email is from another relay. This instance does not allow using another email relay."
            )

        if not life_constants.USER_EMAIL_ENABLE_DISPOSABLE_EMAILS \
                and check_if_email_is_disposable(value):
            logger.info("Request: Signup -> Email is disposable.")
            raise ValueError(
                "Email is disposable. This instance does not allow using disposable emails.",
            )

        return value


class UserUpdate(UserBase):
    password: Optional[str]


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
    alias_image_proxy_user_agent: ProxyUserAgentType

    class Config:
        orm_mode = True


class User(UserBase):
    id: uuid.UUID
    created_at: datetime
    email: Email
    preferences: UserPreferences

    class Config:
        orm_mode = True


class SimpleUserResponseModel(BaseModel):
    user: User
    detail: str
