import uuid
from typing import Optional

from pydantic import BaseModel

__all__ = [
    "AdminUsersResponseModel",
    "AdminSettingsModel",
    "AdminSettingsFilledModel",
]


class AdminUsersResponseUserEmailModel(BaseModel):
    id: uuid.UUID
    address: str

    class Config:
        orm_mode = True


class AdminUsersResponseUserModel(BaseModel):
    id: uuid.UUID
    email: AdminUsersResponseUserEmailModel

    class Config:
        orm_mode = True


class AdminUsersResponseModel(BaseModel):
    users: list[AdminUsersResponseUserModel]


# Since admins can change everything about the settings, we can simply use one model for creating
# / updating and returning the settings model.
class AdminSettingsModel(BaseModel):
    random_email_id_min_length: Optional[int]
    random_email_id_chars: Optional[str]
    random_email_length_increase_on_percentage: Optional[float]
    custom_email_suffix_length: Optional[int]
    custom_email_suffix_chars: Optional[str]
    image_proxy_storage_life_time_in_hours: Optional[int]
    enable_image_proxy: Optional[bool]
    user_email_enable_disposable_emails: Optional[bool]
    user_email_enable_other_relays: Optional[bool]
    allow_statistics: Optional[bool]

    class Config:
        orm_mode = True


class AdminSettingsFilledModel(BaseModel):
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
