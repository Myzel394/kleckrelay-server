import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.database.base import Base
from _mixins import CreationMixin, IDMixin

__all__ = [
    "User",
]


class User(Base, IDMixin, CreationMixin):
    __tablename__ = "User"

    email = relationship(
        "Email",
        backref="user",
        uselist=False,
    )
    encrypted_private_key = sa.Column(
        sa.String,
        nullable=False,
    )
    public_key = sa.Column(
        sa.String,
        nullable=False,
    )
