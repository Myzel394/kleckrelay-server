from pydantic import BaseModel, Field, root_validator

from app.constants import DOMAIN_REGEX, LOCAL_REGEX
from app.life_constants import DOMAIN, MAX_ENCRYPTED_NOTES_SIZE
from app.logger import logger
from app.models.alias import AliasType
from user import User

__all__ = [
    "AliasBase",
    "AliasCreate",
    "AliasUpdate",
    "Alias",
]


class AliasBase(BaseModel):
    is_active: bool = Field(
        default=True,
    )
    encrypted_notes: str = Field(
        max_length=MAX_ENCRYPTED_NOTES_SIZE,
    )


class AliasCreate(AliasBase):
    type: AliasType = Field(
        default=AliasType.RANDOM,
    )
    local: str = Field(
        regex=LOCAL_REGEX,
        default=None,
        description="Only required if type == AliasType.CUSTOM. To avoid collisions, a random "
                    "suffix will be added to the end.",
    )

    @root_validator()
    def validate_type(self, values: dict):
        alias_type = values.get("type")

        logger.info(f"AliasCreate: Validating type {alias_type}.")
        if alias_type == AliasType.RANDOM:
            logger.info("AliasCreate: Type is AliasType.RANDOM")

            if values.get("local") is not None:
                logger.info("AliasCreate: Local is defined, but should not be. Raising exception.")

                raise ValueError("`local` may be None or empty if `type` is AliasType.RANDOM.")
        else:
            logger.info("AliasCreate: Type is AliasType.CUSTOM")


class AliasUpdate(AliasBase):
    is_active: bool = None
    encrypted_notes: str = Field(
        max_length=MAX_ENCRYPTED_NOTES_SIZE,
        default=None,
    )


class Alias(AliasBase):
    id: str
    domain: str = Field(
        regex=DOMAIN_REGEX,
        default=DOMAIN,
    )
    user: User

    class Config:
        orm_mode = True
