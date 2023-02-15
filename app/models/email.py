from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.constants import MAX_EMAIL_LENGTH
from app.database.base import Base
from app.models._mixins import IDMixin
from app.utils.hashes import hash_slowly

__all__ = [
    "Email",
]


class Email(Base, IDMixin):
    __tablename__ = "email"

    if TYPE_CHECKING:
        from .user import User
        address: str
        token: str
        is_verified: bool
        user_id: str
        user: User
    else:
        address = sa.Column(
            sa.String(MAX_EMAIL_LENGTH),
            nullable=False,
            index=True,
            unique=True,
        )
        token = sa.Column(
            sa.String(len(hash_slowly("abc"))),
            nullable=False,
        )
        is_verified = sa.Column(
            sa.Boolean,
            nullable=False,
            default=False,
        )
        user_id = sa.Column(
            UUID(as_uuid=True),
            ForeignKey("user.id"),
        )
