from datetime import datetime
import uuid as uuid_pkg

import sqlalchemy as sa

__all__ = [
    "CreationMixin",
    "UpdateMixin",
    "IDMixin",
]


class CreationMixin:
    created_at = sa.Column(
        sa.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


class UpdateMixin:
    updated_at = sa.Column(
        sa.DateTime,
        default=None,
        onupdate=datetime.utcnow,
    )


class IDMixin:
    id = uuid_pkg.UUID = sa.Column(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
