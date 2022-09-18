from datetime import datetime

from sqlalchemy.orm import declarative_base
import sqlalchemy as sa

__all__ = [
    "Base",
    "CreationMixin",
    "UpdateMixin",
]

Base = declarative_base()


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
