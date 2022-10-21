import base64
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from ._mixins import CreationMixin, IDMixin
from .. import constants, life_constants
from ..database.base import Base
from ..life_constants import API_DOMAIN

__all__ = [
    "ImageProxy",
]


STORAGE_PATH = constants.ROOT_DIR / life_constants.IMAGE_PROXY_STORAGE_PATH


class ImageProxy(Base, IDMixin, CreationMixin):
    __tablename__ = "image_proxy"

    if TYPE_CHECKING:
        from .alias import EmailAlias
        email_alias: EmailAlias
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

    def generate_url(self, url: str) -> str:
        return f"https://{API_DOMAIN}/image-proxy/" \
               f"{base64.b64encode(url.encode('utf-8')).decode('utf-8')}" \
               f"?proxy_id={self.id}"

    def should_download(self) -> bool:
        return not self.has_downloaded_image_expired \
               and (not self.path or not self.absolute_path.exists())

    def is_available(self) -> bool:
        return not self.has_downloaded_image_expired and self.path and self.absolute_path.exists()

    @property
    def has_downloaded_image_expired(self) -> bool:
        expire_date = self.created_at + \
                      timedelta(seconds=life_constants.IMAGE_PROXY_TIMEOUT_IN_SECONDS)

        return expire_date > datetime.utcnow()

    @property
    def absolute_path(self) -> Path:
        return STORAGE_PATH / self.path
