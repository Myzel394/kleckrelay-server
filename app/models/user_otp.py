import enum
import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base
from ._mixins import CreationMixin, IDMixin

__all__ = [
    "UserOTP"
]


class OTPStatusType(str, enum.Enum):
    AVAILABLE = "available"
    AWAITING_VERIFICATION = "awaiting-verification"


class UserOTP(Base, IDMixin, CreationMixin):
    __tablename__ = "user_otp"

    if TYPE_CHECKING:
        from app.models.user import User
        user_id: uuid.UUID
        user: User
        secret: str
        status: OTPStatusType
    else:
        user_id = sa.Column(
            UUID(as_uuid=True),
            sa.ForeignKey("user.id"),
            nullable=False
        )
        secret = sa.Column(
            sa.String,
            nullable=False
        )
        status = sa.Column(
            sa.Enum(OTPStatusType),
            default=OTPStatusType.AWAITING_VERIFICATION,
        )

    @property
    def is_verified(self) -> bool:
        return self.status == OTPStatusType.AVAILABLE
