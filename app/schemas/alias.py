from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, root_validator

from app.controllers import global_settings as settings
from app.constants import LOCAL_REGEX, MAX_LOCAL_LENGTH
from app import life_constants
from app.logger import logger
from app.models.alias import AliasType, ImageProxyFormatType
from app.models.enums.alias import ProxyUserAgentType

__all__ = [
    "AliasCreate",
    "AliasUpdate",
    "AliasList",
    "AliasDetail",
]


class AliasBase(BaseModel):
    is_active: Optional[bool] = None
    encrypted_notes: str = Field(
        max_length=life_constants.MAX_ENCRYPTED_NOTES_SIZE,
        default="",
    )

    # Preferences
    pref_remove_trackers: Optional[bool] = None
    pref_create_mail_report: Optional[bool] = None
    pref_proxy_images: Optional[bool] = None
    pref_image_proxy_format: Optional[ImageProxyFormatType] = None
    pref_proxy_user_agent: Optional[ProxyUserAgentType] = None
    pref_expand_url_shorteners: Optional[bool] = None


class AliasCreate(AliasBase):
    type: AliasType = AliasType.RANDOM
    local: str = Field(
        regex=LOCAL_REGEX,
        default=None,
        max_length=MAX_LOCAL_LENGTH,
        description="Only required if type == AliasType.CUSTOM. To avoid collisions, a random "
                    "suffix will be added to the end.",
    )

    @root_validator()
    def validate_type(cls, values: dict):
        alias_type = values.get("type")

        logger.info(f"AliasCreate: Validating type {alias_type}.")
        if alias_type == AliasType.RANDOM:
            logger.info("AliasCreate: Type is AliasType.RANDOM")

            if values.get("local") is not None:
                logger.info("AliasCreate: Local is defined, but should not be. Raising exception.")

                raise ValueError("`local` may be None or empty if `type` is AliasType.RANDOM.")
        elif alias_type == AliasType.CUSTOM:
            logger.info("AliasCreate: Type is AliasType.CUSTOM")

            if not values.get("local"):
                logger.info("AliasCreate: Local is not defined, but shouldbe. Raising exception.")

                raise ValueError("`local` may not be None or empty if `type` is AliasType.CUSTOM.")

        return values


class AliasUpdate(AliasBase):
    pass


class AliasList(BaseModel):
    is_active: bool
    id: UUID
    domain: str
    local: str
    type: AliasType
    encrypted_notes: str

    class Config:
        orm_mode = True


class AliasDetail(AliasBase):
    id: UUID
    domain: str
    local: str
    type: AliasType

    class Config:
        orm_mode = True
