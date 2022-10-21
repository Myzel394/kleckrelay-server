import enum
from typing import Any, Optional, TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app import constants, gpg_handler
from app.database.base import Base
from ._mixins import CreationMixin, IDMixin

__all__ = [
    "LanguageType",
    "User",
]


class LanguageType(str, enum.Enum):
    EN_US = "en_US"


class User(Base, IDMixin, CreationMixin):
    __tablename__ = "user"

    if TYPE_CHECKING:
        from .email import Email
        from .alias import EmailAlias
        from .email_login import EmailLoginToken
        from .email_report import EmailReport
        from .user_preferences import UserPreferences
        email: Email
        language: LanguageType
        public_key: Optional[str]
        encrypted_notes: Optional[str]
        encrypted_password: Optional[str]
        email_aliases: list[EmailAlias]
        email_reports: list[EmailReport]
        email_login_token: EmailLoginToken
        preferences: UserPreferences
    else:
        email = relationship(
            "Email",
            backref="user",
            uselist=False,
        )
        language = sa.Column(
            sa.Enum(LanguageType),
            default=LanguageType.EN_US,
        )
        public_key = sa.Column(
            sa.String(constants.PUBLIC_KEY_MAX_LENGTH),
            default=None,
            nullable=True,
        )
        encrypted_notes = sa.Column(
            sa.String(constants.ENCRYPTED_NOTES_MAX_LENGTH),
            default=None,
            nullable=True,
        )
        encrypted_password = sa.Column(
            sa.String(constants.ENCRYPTED_PASSWORD_MAX_LENGTH),
            default=None,
            nullable=True,
        )
        email_aliases = relationship(
            "EmailAlias",
            backref="user",
        )
        email_reports = relationship(
            "EmailReport",
            backref="user",
        )
        email_login_token = relationship(
            "EmailLoginToken",
            backref="user",
            uselist=False,
        )
        preferences = relationship(
            "UserPreferences",
            backref="user",
            uselist=False,
        )

    def to_jwt_object(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
        }

    def encrypt(self, message: str) -> str:
        return gpg_handler.encrypt_message(message, self.public_key)
