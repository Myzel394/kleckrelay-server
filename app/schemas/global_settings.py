from pydantic import BaseModel, Field

__all__ = [
    "GlobalSettingsModel"
]


# This model is only used internally for other schemes to use.
class GlobalSettingsModel(BaseModel):
    random_email_id_min_length: int
    random_email_id_chars: str
    random_email_length_increase_on_percentage: float
    custom_email_suffix_length: int
    custom_email_suffix_chars: str
    image_proxy_storage_life_time_in_hours: int
    enable_image_proxy: bool
    user_email_enable_disposable_emails: bool
    user_email_enable_other_relays: bool
    allow_statistics: bool
    allow_alias_deletion: bool
