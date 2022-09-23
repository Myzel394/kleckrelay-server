from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.database.base import Base
from ._mixins import CreationMixin, IDMixin
from ..constants import ENCRYPTED_PASSWORD_LENGTH

__all__ = [
    "User",
]


class User(Base, IDMixin, CreationMixin):
    __tablename__ = "user"

    if TYPE_CHECKING:
        from .email import Email
        from .alias import EmailAlias
        from .email_login import EmailLoginToken
        email: Email
        encrypted_password: str
        email_aliases: list[EmailAlias]
        email_login_token: EmailLoginToken
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
        email_aliases = relationship(
            "EmailAlias",
            backref="user",
        )
        email_login_token = relationship(
            "EmailLoginToken",
            backref="user",
            uselist=False,
        )
