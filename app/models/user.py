from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.constants import ENCRYPTED_PASSWORD_LENGTH
from app.database.base import Base
from _mixins import CreationMixin, IDMixin

__all__ = [
    "User",
]


class User(Base, IDMixin, CreationMixin):
    __tablename__ = "User"

    if TYPE_CHECKING:
        from .email import Email
        email: Email
        encrypted_password: str
    else:
        email = relationship(
            "Email",
            backref="user",
            uselist=False,
        )
        encrypted_password = sa.Column(
            sa.String(ENCRYPTED_PASSWORD_LENGTH),
            nullable=False,
        )
