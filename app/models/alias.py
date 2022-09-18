import sqlalchemy as sa
from sqlalchemy.orm import relationship

from _mixins import Base, CreationMixin, UpdateMixin

__all__ = [
    "EmailAlias",
]


class EmailAlias(Base, CreationMixin, UpdateMixin):
    __tablename__ = "email_alias"

    user = relationship(
        "User",
        back_populates="email_aliases"
    )
    local = sa.Column(
        sa.String,
        nullable=False,
        index=True,
    )
    domain = sa.Column(
        sa.String,
        nullable=False,
        index=True,
    )
    is_active = sa.Column(
        sa.Boolean,
        default=True,
        nullable=False,
    )
    encrypted_notes = sa.Column(
        sa.String,
        nullable=False,
        default="",
    )

