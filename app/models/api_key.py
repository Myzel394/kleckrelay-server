import enum
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base
from ._mixins import IDMixin, CreationMixin
from .enums.api_key import APIKeyScope
from ..utils.hashes import hash_fast, hash_slowly

__all__ = [
    "APIKey"
]


class APIKey(Base, IDMixin):
    __tablename__ = "api_key"

    if TYPE_CHECKING:
        from .user import User

        user_id: str
        user: User
        expires_at: datetime
        hashed_key: str
        scopes: list[APIKeyScope]
    else:
        user_id = sa.Column(
            UUID(as_uuid=True),
            ForeignKey("user.id"),
        )
        expires_at = sa.Column(
            sa.DateTime,
            nullable=False,
        )
        hashed_key = sa.Column(
            sa.String(len(hash_fast("1234"))),
            nullable=False,
        )
        scopes = sa.Column(
            sa.ARRAY(sa.Enum(APIKeyScope)),
            nullable=False,
        )
