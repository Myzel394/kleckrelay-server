from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base
from app.models import IDMixin
from app.models.enums.alias import ImageProxyFormatType, ProxyUserAgentType

__all__ = [
    "UserPreferences",
]


class UserPreferences(Base, IDMixin):
    __tablename__ = "user_preferences"

    if TYPE_CHECKING:
        from uuid import UUID as UUID_python
        from .user import User
        user_id: UUID_python
        user: User
        alias_remove_trackers: bool
        alias_create_mail_report: bool
        alias_proxy_images: bool
        alias_image_proxy_format: ImageProxyFormatType
        alias_proxy_user_agent: ProxyUserAgentType
        alias_expand_url_shorteners: bool
    else:
        user_id = sa.Column(
            UUID(as_uuid=True),
            ForeignKey("user.id"),
        )

        alias_remove_trackers = sa.Column(
            sa.Boolean,
            default=True,
        )
        alias_create_mail_report = sa.Column(
            sa.Boolean,
            default=True,
        )
        alias_proxy_images = sa.Column(
            sa.Boolean,
            default=True,
        )
        alias_image_proxy_format = sa.Column(
            sa.Enum(ImageProxyFormatType),
            default=ImageProxyFormatType.JPEG,
        )
        alias_proxy_user_agent = sa.Column(
            sa.Enum(ProxyUserAgentType),
            default=ProxyUserAgentType.FIREFOX,
        )
        alias_expand_url_shorteners = sa.Column(
            sa.Boolean,
            default=True,
        )
