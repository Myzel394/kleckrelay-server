import sqlalchemy as sa
from sqlalchemy.orm import relationship, Session

from app.authentication.email_login import hash_token
from app.constants import (
    EMAIL_LOGIN_TOKEN_SAME_REQUEST_TOKEN_LENGTH,
)
from app.database.base import Base
from app.models._mixins import CreationMixin, IDMixin

__all__ = [
    "EmailLoginToken",
]


class EmailLoginToken(Base, IDMixin, CreationMixin):
    __tablename__ = "email_login_token"

    user = relationship(
        "User",
        backref="email_login_token",
        uselist=False,
    )
    hashed_token = sa.Column(
        sa.String(len(hash_token("1234"))),
        nullable=False,
    )
    hashed_same_request_token = sa.Column(
        sa.String(hash_token("1234")),
        nullable=False,
    )
    tries = sa.Column(
        sa.SmallInteger(),
        nullable=False,
        default=0,
    )
