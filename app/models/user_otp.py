import enum
import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base
from ._mixins import IDMixin


class StatusType(str, enum.Enum):
    AVAILABLE = "available"
    AWAITING_VERIFICATION = "awaiting-verification"


class UserOTP(Base, IDMixin):
    if TYPE_CHECKING:
        from app.models.user import User
        user_id: uuid.UUID
        user: User
        secret: str
        status: "awaiting-verification" | "available"
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
            sa.Enum(StatusType),
            default=StatusType.AWAITING_VERIFICATION,
            nullable=False
        )

    @property
    def is_verified(self) -> bool:
        return self.status == StatusType.AVAILABLE
