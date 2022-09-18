import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.life_constants import MAX_ENCRYPTED_NOTES_SIZE
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
    encrypted_notes = sa.Column(
        sa.String(MAX_ENCRYPTED_NOTES_SIZE),
        nullable=False,
        default="",
    )


class DeletedEmailAlias(Base):
    """Store all deleted alias to make sure they will not be reused, so that new owner won't
    receive emails from old aliases."""

    email = sa.Column(
        sa.String(255 + 64 + 1 + 20),
        unique=True,
        nullable=False,
    )
