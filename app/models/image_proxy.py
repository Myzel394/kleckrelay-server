import base64

import sqlalchemy as sa

from ._mixins import IDMixin
from ..database.base import Base
from ..life_constants import DOMAIN

__all__ = [
    "ImageProxy",
]


class ImageProxy(Base, IDMixin):
    __tablename__ = "image_proxy"

    hashed_url = sa.Column(
        sa.String(),
        nullable=False,
        unique=True,
    )
    path = sa.Column(
        sa.String(),
        nullable=True,
        default=None,
    )
    
    def generate_url(self, url: str) -> str:
        return f"https://{DOMAIN}/image-proxy/" \
               f"{base64.b64encode(url.encode('utf-8')).decode('utf-8')}"
