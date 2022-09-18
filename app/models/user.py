from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
import sqlalchemy as sa
from _mixins import Base, CreationMixin

__all__ = [
    "User",
]


class User(SQLAlchemyBaseUserTableUUID, Base, CreationMixin):
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
