import base64
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from ._mixins import IDMixin
from ..database.base import Base
from ..life_constants import DOMAIN

__all__ = [
    "ImageProxy",
]


class ImageProxy(Base, IDMixin):
    __tablename__ = "image_proxy"

    if TYPE_CHECKING:
        from .alias import EmailAlias
        alias: EmailAlias
        alias_id: str
        hashed_url: str
        path: str
    else:
        alias_id = sa.Column(
            UUID(as_uuid=True),
            ForeignKey("email_alias.id"),
        )
        hashed_url = sa.Column(
            sa.String(),
            nullable=False,
        )
        path = sa.Column(
            sa.String(),
            nullable=True,
            default=None,
        )
        downloaded_at = sa.Column(
            sa.DateTime(),
            nullable=True,
        )
    
    def generate_url(self, url: str) -> str:
        return f"https://{DOMAIN}/image-proxy/" \
               f"{base64.b64encode(url.encode('utf-8')).decode('utf-8')}" \
               f"?proxy_id={self.id}"
