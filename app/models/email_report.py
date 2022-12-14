from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app import constants
from app.database.base import Base
from app.models import IDMixin

__all__ = [
    "EmailReport",
]


class EmailReport(Base, IDMixin):
    __tablename__ = "email_report"

    if TYPE_CHECKING:
        from .user import User
        user_id: str
        user: User
        encrypted_content: str
    else:
        user_id = sa.Column(
            UUID(as_uuid=True),
            ForeignKey("user.id"),
        )
        encrypted_content = sa.Column(
            sa.String(constants.EMAIL_REPORT_ENCRYPTED_CONTENT_MAX_LENGTH),
            nullable=False,
        )
