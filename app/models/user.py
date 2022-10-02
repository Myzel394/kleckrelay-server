from typing import Any, Optional, TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app import constants
from app.database.base import Base
from ._mixins import CreationMixin, IDMixin

__all__ = [
    "User",
]


class User(Base, IDMixin, CreationMixin):
    __tablename__ = "user"

    if TYPE_CHECKING:
        from .email import Email
        from .alias import EmailAlias
        from .email_login import EmailLoginToken
        from .email_report import EmailReport
        email: Email
        public_key: Optional[str]
        encrypted_private_key: Optional[str]
        hashed_password: Optional[str]
        email_aliases: list[EmailAlias]
        email_reports: list[EmailReport]
        email_login_token: EmailLoginToken
    else:
        email = relationship(
            "Email",
            backref="user",
            uselist=False,
        )
        public_key = sa.Column(
            sa.String(constants.PUBLIC_KEY_MAX_LENGTH),
            default=None,
            nullable=True,
        )
        encrypted_private_key = sa.Column(
            sa.String(constants.ENCRYPTED_PRIVATE_KEY_MAX_LENGTH),
            default=None,
            nullable=True,
        )
        hashed_password = sa.Column(
            sa.String(),
            default=None,
            nullable=True,
        )
        email_aliases = relationship(
            "EmailAlias",
            backref="user",
        )
        emai_reports = relationship(
            "EmailReport",
            backref="user",
        )
        email_login_token = relationship(
            "EmailLoginToken",
            backref="user",
            uselist=False,
        )

    def to_jwt_object(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "created_at": self.created_at.isoformat(),
            "email": {
                "address": self.email.address,
                "is_verified": self.email.is_verified
            },
        }
