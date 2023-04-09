from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, root_validator, validator

from app import constants, gpg_handler
from app.models.enums.alias import ImageProxyFormatType, ProxyUserAgentType

__all__ = [
    "UserPreferencesUpdate",
    "FindPublicKeyResponseModel"
]


class UserPreferencesUpdate(BaseModel):
    email_gpg_public_key: Optional[str] = Field(
        None,
        regex=constants.PUBLIC_KEY_REGEX,
        max_length=constants.PUBLIC_KEY_MAX_LENGTH,
    )
    alias_remove_trackers: bool = None
    alias_create_mail_report: bool = None
    alias_proxy_images: bool = None
    alias_image_proxy_format: ImageProxyFormatType = None
    alias_proxy_user_agent: ProxyUserAgentType = None
    alias_expand_url_shortener: bool = None
    alias_reject_on_privacy_leak: bool = None

    update_all_instances: bool = Field(default=False)

    @root_validator()
    def validate_any_value_set(cls, values: dict) -> dict:
        data = values.copy()
        data.pop("update_all_instances", None)

        if all(
            value is None
            for value in data.values()
        ):
            raise ValueError("You must set at least one preference to update.")

        return values

    @validator("email_gpg_public_key")
    def validate_email_gpg_public_key(cls, value: Optional[str]) -> Optional[str]:
        if not value:
            return

        value = value.strip()
        message = f"PGP verification. Your public key is: {value}"

        try:
            result = gpg_handler.encrypt_message(message, value)

            if not result.ok:
                raise ValueError(
                    "This is not a valid PGP public key; we could not encrypt a test message."
                )
        except ValueError:
            raise ValueError(
                "This is not a valid PGP public key; we could not encrypt a test message."
            )

        return value


class FindPublicKeyResponseModel(BaseModel):
    public_key: str
    type: str
    created_at: date
