from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.life_constants import MAX_ENCRYPTED_NOTES_SIZE
from ._mixins import CreationMixin, IDMixin
from .constants.alias import PROXY_USER_AGENT_STRING_MAP
from .enums.alias import AliasType, ImageProxyFormatType, ProxyUserAgentType
from ..mixins.model_preference import ModelPreference

__all__ = [
    "EmailAlias",
]


class EmailAlias(Base, IDMixin, ModelPreference):
    __tablename__ = "email_alias"

    if TYPE_CHECKING:
        from .user import User
        from .image_proxy import ImageProxy

        local: str
        domain: str
        type: AliasType
        is_active: bool
        encrypted_notes: str
        user_id: str
        user: User
        image_proxies: list[ImageProxy]

        pref_remove_trackers: bool
        pref_create_mail_report: bool
        pref_proxy_images: bool
        pref_image_proxy_format: ImageProxyFormatType
        pref_proxy_user_agent: ProxyUserAgentType
        pref_expand_url_shorteners: bool
    else:
        local = sa.Column(
            sa.String(64),
            nullable=False,
            index=True,
        )
        domain = sa.Column(
            sa.String(255),
            nullable=False,
            index=True,
        )
        type = sa.Column(
            sa.Enum(AliasType),
            default=AliasType.RANDOM,
        )
        is_active = sa.Column(
            sa.Boolean,
            default=True,
            nullable=False,
        )
        encrypted_notes = sa.Column(
            sa.String(MAX_ENCRYPTED_NOTES_SIZE),
            nullable=False,
            default="",
        )
        user_id = sa.Column(
            UUID(as_uuid=True),
            ForeignKey("user.id"),
        )
        image_proxies = relationship(
            "ImageProxy",
            backref="email_alias",
        )

        pref_remove_trackers = sa.Column(
            sa.Boolean,
            default=None,
            nullable=True,
        )
        pref_create_mail_report = sa.Column(
            sa.Boolean,
            default=None,
            nullable=True,
        )
        pref_proxy_images = sa.Column(
            sa.Boolean,
            default=None,
            nullable=True,
        )
        pref_image_proxy_format = sa.Column(
            sa.Enum(ImageProxyFormatType),
            default=None,
            nullable=True,
        )
        pref_proxy_user_agent = sa.Column(
            sa.Enum(ProxyUserAgentType),
            default=None,
            nullable=True,
        )
        pref_expand_url_shorteners = sa.Column(
            sa.Boolean,
            default=None,
            nullable=True,
        )

    def _get_user_preference_prefix(self) -> str:
        return "alias_"

    def get_user_agent_string(self) -> str:
        return PROXY_USER_AGENT_STRING_MAP[self.proxy_user_agent]

    @property
    def address(self) -> str:
        return f"{self.local}@{self.domain}"

    @property
    def remove_trackers(self) -> bool:
        return self.get_preference_value("remove_trackers")

    @property
    def create_mail_report(self) -> bool:
        return self.get_preference_value("create_mail_report")

    @property
    def proxy_images(self) -> bool:
        return self.get_preference_value("proxy_images")

    @property
    def proxy_image_format(self) -> ImageProxyFormatType:
        return self.get_preference_value("image_proxy_format")

    @property
    def proxy_user_agent(self) -> ProxyUserAgentType:
        return self.get_preference_value("proxy_user_agent")

    @property
    def expand_url_shorteners(self) -> bool:
        return self.get_preference_value("expand_url_shorteners")


class DeletedEmailAlias(Base, IDMixin, CreationMixin):
    """Store all deleted alias to make sure they will not be reused, so that new owner won't
    receive emails from old aliases."""

    __tablename__ = "deleted_email_alias"

    if TYPE_CHECKING:
        email: str
    else:
        email = sa.Column(
            sa.String(255 + 64 + 1 + 20),
            unique=True,
            nullable=False,
        )
