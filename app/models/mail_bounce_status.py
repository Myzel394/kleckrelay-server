from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import Sequence

from app import constants
from app.database.base import Base
from ._mixins import IDMixin, CreationMixin
from .enums.mail_bounce_status import StatusType

__all__ = [
    "MailBounceStatus"
]

TABLE_ID = Sequence('table_id_seq', start=1)


class MailBounceStatus(Base, CreationMixin):
    __tablename__ = "mail_bounce_status"

    if TYPE_CHECKING:
        id: int
        from_address: str
        to_address: str
        status: StatusType
    else:
        # We need to save as most space as possible for the VERP address,
        # so we use an incrementing integer as primary key
        id = sa.Column(
            sa.Integer,
            primary_key=True,
            unique=True,
            index=True,
        )
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
        return self.created_at < datetime.now() - constants.BOUNCE_MAX_TIME
