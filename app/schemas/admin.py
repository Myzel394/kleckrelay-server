import uuid
from typing import Optional

from pydantic import BaseModel, Field

__all__ = [
    "AdminUsersResponseModel",
    "AdminGlobalSettingsDisabledResponseModel"
]

SMALL_INTEGER_LIMIT = 32_767
INTEGER_LIMIT = 2_147_483_647


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


class AdminGlobalSettingsDisabledResponseModel(BaseModel):
    detail: str
    code: str = "error:settings:global_settings_disabled"


class AdminUpdateGlobalSettingsModel(BaseModel):
    random_email_id_min_length: Optional[int] = Field(None, ge=1, le=SMALL_INTEGER_LIMIT)
    random_email_id_chars: Optional[str] = Field(None, max_length=1023)
    random_email_length_increase_on_percentage: Optional[float] = Field(None, ge=0.0, le=1.0)
    custom_email_suffix_length: Optional[int] = Field(None, ge=1, le=SMALL_INTEGER_LIMIT)
    custom_email_suffix_chars: Optional[str] = Field(None, max_length=1023)
    image_proxy_storage_life_time_in_hours: Optional[int] = Field(None, ge=1, le=INTEGER_LIMIT)
    enable_image_proxy: Optional[bool] = None
    user_email_enable_disposable_emails: Optional[bool] = None
    user_email_enable_other_relays: Optional[bool] = None
    allow_statistics: Optional[bool] = None
    allow_alias_deletion: Optional[bool] = None
    max_aliases_per_user: Optional[int] = Field(None, ge=0, le=INTEGER_LIMIT)
