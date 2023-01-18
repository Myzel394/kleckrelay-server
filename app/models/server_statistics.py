from typing import TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.database.base import Base
from ._mixins import CreationMixin, IDMixin
from .user import User
from .alias import EmailAlias

__all__ = [
    "ServerStatistics"
]


class ServerStatistics(Base, IDMixin, CreationMixin):
    __tablename__ = "server_statistics"

    if TYPE_CHECKING:
        sent_emails_amount: int
        proxied_images_amount: int
        expanded_urls_amount: int
        trackers_removed_amount: int
    else:
        sent_emails_amount = sa.Column(
            sa.Integer(),
            default=0,
        )
        proxied_images_amount = sa.Column(
            sa.Integer(),
            default=0,
        )
        expanded_urls_amount = sa.Column(
            sa.Integer(),
            default=0,
        )
        trackers_removed_amount = sa.Column(
            sa.Integer(),
            default=0,
        )

    @staticmethod
    def get_users_amount(db: Session, /) -> int:
        return db.query(User).count()

    @staticmethod
    def get_aliases_amount(db: Session, /) -> int:
        return db.query(EmailAlias).count()

