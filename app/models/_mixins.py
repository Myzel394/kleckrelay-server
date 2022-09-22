from datetime import datetime
import uuid as uuid_pkg
from typing import TYPE_CHECKING
from sqlalchemy.dialects.postgresql import UUID

import sqlalchemy as sa

__all__ = [
    "CreationMixin",
    "UpdateMixin",
    "IDMixin",
]


class CreationMixin:
    if TYPE_CHECKING:
        created_at: datetime
    else:
        created_at = sa.Column(
            sa.DateTime,
            default=datetime.utcnow,
            nullable=False,
        )


class UpdateMixin:
    if TYPE_CHECKING:
        updated_at: datetime
    else:
        updated_at = sa.Column(
            sa.DateTime,
            default=None,
            onupdate=datetime.utcnow,
        )


class IDMixin:
    if TYPE_CHECKING:
        id: str
    else:
        id = sa.Column(
            UUID(as_uuid=True),
            default=uuid_pkg.uuid4,
            primary_key=True,
            unique=True,
            index=True,
            nullable=False,
        )
