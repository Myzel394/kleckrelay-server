import sqlalchemy as sa

from app.constants import MAX_EMAIL_LENGTH
from app.database.base import Base
from app.models._mixins import IDMixin, CreationMixin
from app.utils import hash_slowly

__all__ = [
    "Email",
]


class Email(Base, IDMixin, CreationMixin):
    __tablename__ = "email"

    address = sa.Column(
        sa.String(MAX_EMAIL_LENGTH),
        nullable=False,
        index=True,
        unique=True,
    )
    is_verified = sa.Column(
        sa.Boolean,
        default=False,
    )
    hashed_token = sa.Column(
        sa.String(len(hash_slowly("abc"))),
        nullable=False,
    )
