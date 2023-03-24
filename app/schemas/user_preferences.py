from pydantic import BaseModel, Field, root_validator

from app.models.enums.alias import ImageProxyFormatType, ProxyUserAgentType

__all__ = [
    "UserPreferencesUpdate",
]


class UserPreferencesUpdate(BaseModel):
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
