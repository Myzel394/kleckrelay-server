from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
import sqlalchemy as sa
from app.database.base import Base
from _mixins import CreationMixin, IDMixin

__all__ = [
    "User",
]


class User(Base, IDMixin, CreationMixin):
    __tablename__ = "User"

    email = sa.Column(
        sa.String,
        unique=True,
        index=True,
        nullable=False
    )
    encrypted_private_key = sa.Column(
        sa.String,
        nullable=False,
    )
    public_key = sa.Column(
        sa.String,
        nullable=False,
    )
