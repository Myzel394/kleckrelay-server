import enum
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base
from app.life_constants import MAX_ENCRYPTED_NOTES_SIZE
from ._mixins import CreationMixin, UpdateMixin, IDMixin

__all__ = [
    "AliasType",
    "EmailAlias",
]


class AliasType(enum.Enum):
    RANDOM = "RANDOM"
    CUSTOM = "CUSTOM"


class EmailAlias(Base, IDMixin):
    __tablename__ = "email_alias"

    if TYPE_CHECKING:
        from .user import User
        local: str
        domain: str
        is_active: bool
        encrypted_notes: str
        user: User
        user_id: str
    else:
        local = sa.Column(
            sa.String(64),
            nullable=False,
            index=True,
        )
        domain = sa.Column(
            sa.String(255),
            nullable=False,
            index=True,
        )
        type = sa.Column(
            sa.Enum(AliasType),
            default=AliasType.RANDOM,
        )
        is_active = sa.Column(
            sa.Boolean,
            default=True,
            nullable=False,
        )
        encrypted_notes = sa.Column(
            sa.String(MAX_ENCRYPTED_NOTES_SIZE),
            nullable=False,
            default="",
        )
        user_id = sa.Column(
            UUID(as_uuid=True),
            ForeignKey("user.id"),
        )


class DeletedEmailAlias(Base, IDMixin, CreationMixin):
    """Store all deleted alias to make sure they will not be reused, so that new owner won't
    receive emails from old aliases."""

    __tablename__ = "deleted_email_alias"

    if TYPE_CHECKING:
        email: str
    else:
        email = sa.Column(
            sa.String(255 + 64 + 1 + 20),
            unique=True,
            nullable=False,
        )
