from uuid import UUID

from pydantic import BaseModel, Field, root_validator

from app.constants import LOCAL_REGEX, MAX_LOCAL_LENGTH
from app.life_constants import CUSTOM_EMAIL_SUFFIX_LENGTH, MAX_ENCRYPTED_NOTES_SIZE
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
    is_active: bool = Field(
        default=True,
    )
    encrypted_notes: str = Field(
        max_length=MAX_ENCRYPTED_NOTES_SIZE,
        default="",
    )

    # Preferences
    remove_trackers: bool = Field(
        default=None,
    )
    create_mail_report: bool = Field(
        default=None,
    )
    proxy_images: bool = Field(
        default=None,
    )
    image_proxy_format: ImageProxyFormatType = Field(
        default=None,
    )
    image_proxy_user_agent: ProxyUserAgentType = Field(
        default=None,
    )


class AliasCreate(AliasBase):
    type: AliasType = Field(
        default=AliasType.RANDOM,
    )
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
        else:
            logger.info("AliasCreate: Type is AliasType.CUSTOM")
            # Validate length

            if len(values.get("local", "")) > \
                    (max_length := MAX_LOCAL_LENGTH - CUSTOM_EMAIL_SUFFIX_LENGTH - 1):
                raise ValueError(
                    f"`local` is too long. It should be at most {max_length} characters long."
                )

        return values


class AliasUpdate(AliasBase):
    is_active: bool = None
    encrypted_notes: str = Field(
        max_length=MAX_ENCRYPTED_NOTES_SIZE,
        default=None,
    )


class AliasList(BaseModel):
    is_active: bool
    id: UUID
    domain: str
    local: str

    class Config:
        orm_mode = True


class AliasDetail(AliasBase):
    id: UUID
    domain: str
    local: str

    class Config:
        orm_mode = True
