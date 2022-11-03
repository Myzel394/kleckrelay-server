from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app import life_constants
from app.database.base import Base
from app.models._mixins import CreationMixin, IDMixin
from app.utils import hash_fast

__all__ = [
    "EmailLoginToken",
]


class EmailLoginToken(Base, IDMixin, CreationMixin):
    __tablename__ = "email_login_token"

    if TYPE_CHECKING:
        from .user import User
        token: str
        hashed_same_request_token: str
        tries: int
        user: User
        user_id: str
    else:
        token = sa.Column(
            sa.String(life_constants.EMAIL_LOGIN_TOKEN_LENGTH),
            nullable=False,
        )
        hashed_same_request_token = sa.Column(
            sa.String(len(hash_fast("1234"))),
            nullable=True,
        )
        tries = sa.Column(
            sa.SmallInteger(),
            nullable=False,
            default=0,
        )
        user_id = sa.Column(
            UUID(as_uuid=True),
            ForeignKey("user.id"),
        )
