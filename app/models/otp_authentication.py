import uuid
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base
from ._mixins import IDMixin, CreationMixin
from .. import constants
from ..utils.hashes import hash_fast

__all__ = [
    "OTPAuthentication"
]


class OTPAuthentication(Base, IDMixin, CreationMixin):
    __tablename__ = "otp_authentication"

    if TYPE_CHECKING:
        from app.models.user import User
        user_id: uuid.UUID
        user: User
        tries: int
        hashed_cors_token: str
    else:
        user_id = sa.Column(
            UUID(as_uuid=True),
            sa.ForeignKey("user.id"),
            nullable=False
        )
        tries = sa.Column(
            sa.SmallInteger,
            nullable=False,
            default=0
        )
        hashed_cors_token = sa.Column(
            sa.String(len(hash_fast("1234"))),
            nullable=False
        )

    @property
    def is_expired(self) -> bool:
        return self.created_at >= datetime.now() - constants.OTP_TIMEOUT
