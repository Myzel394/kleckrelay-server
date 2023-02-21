from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa

from app import constants
from app.database.base import Base
from ._mixins import IDMixin, CreationMixin
from .enums.mail_bounce_status import StatusType

__all__ = [
    "MailBounceStatus"
]


class MailBounceStatus(Base, IDMixin, CreationMixin):
    __tablename__ = "mail_bounce_status"

    if TYPE_CHECKING:
        from_address: str
        to_address: str
        status: StatusType
    else:
        from_address = sa.Column(
            sa.String(255),
        )
        to_address = sa.Column(
            sa.String(255),
        )
        status = sa.Column(
            sa.Enum(StatusType),
            default=StatusType.FORWARDING,
        )

    @property
    def is_expired(self) -> bool:
        return self.created_at < datetime.now() - constants.MAX_VERP_TIME
