from typing import Any, TYPE_CHECKING, Union

from sqlalchemy.orm import relationship

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
        email: Email
        email_aliases: list[EmailAlias]
        email_login_token: EmailLoginToken
    else:
        email = relationship(
            "Email",
            backref="user",
            uselist=False,
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

    def to_jwt_object(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "created_at": self.created_at.isoformat(),
            "email": {
                "address": self.email.address,
                "is_verified": self.email.is_verified
            },
        }
