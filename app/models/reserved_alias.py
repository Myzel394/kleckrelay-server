from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import InstrumentedList

from app.database.base import Base
from ._mixins import IDMixin

if TYPE_CHECKING:
    from .user import User

__all__ = [
    "ReservedAlias",
]


class ReservedAliasUser(Base, IDMixin):
    __tablename__ = "m2m_reserved_alias_user"

    reserved_alias_id = Column(UUID(as_uuid=True), ForeignKey("reserved_alias.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))


class ReservedAlias(Base, IDMixin):
    __tablename__ = "reserved_alias"

    if TYPE_CHECKING:
        local: str
        domain: str
        is_active: bool

        # Where the alias will be forwarded to
        users: InstrumentedList["User"]
    else:
        local = sa.Column(
            sa.String(64),
            nullable=False,
            index=True,
        )
        domain = sa.Column(
            sa.String(255),
            nullable=False,
            index=True,
        )
        is_active = sa.Column(
            sa.Boolean,
            default=True,
            nullable=False,
        )

        users = relationship(
            "User",
            secondary=ReservedAliasUser.__table__,
            back_populates="reserved_aliases",
        )