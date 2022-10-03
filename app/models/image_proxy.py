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
    )
    path = sa.Column(
        sa.String(),
        nullable=True,
        default=None,
    )
    
    @property
    def url(self) -> str:
        return f"https://{DOMAIN}/image-proxy/{self.hashed_url}"
