from pydantic import BaseModel

__all__ = [
    "GlobalSettingsModel"
]


# Since admins can change everything about the settings, we can simply use one model for creating
# / updating and returning the settings model.
class GlobalSettingsModel(BaseModel):
    random_email_id_min_length: int
    random_email_id_chars: str
    random_email_length_increase_on_percentage: float
    custom_email_suffix_length: int
    custom_email_suffix_chars: str
    image_proxy_storage_life_time_in_hours: int
    enable_image_proxy: bool
    enable_image_proxy_storage: bool
    user_email_enable_disposable_emails: bool
    user_email_enable_other_relays: bool
    allow_statistics: bool
    allow_alias_deletion: bool
    max_aliases_per_user: int
    allow_registrations: bool

    class Config:
        orm_mode = True
