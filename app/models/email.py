from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.constants import MAX_EMAIL_LENGTH
from app.database.base import Base
from app.models._mixins import IDMixin, CreationMixin
from app.utils import hash_slowly

__all__ = [
    "Email",
]


class Email(Base, IDMixin, CreationMixin):
    __tablename__ = "email"

    if TYPE_CHECKING:
        from .user import User
        address: str
        token: str
        verified_at: datetime
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
        verified_at = sa.Column(
            sa.DateTime,
            nullable=True,
            default=None,
        )
        user_id = sa.Column(
            UUID(as_uuid=True),
            ForeignKey("user.id"),
        )

    @property
    def is_verified(self) -> bool:
        return self.verified_at is not None
