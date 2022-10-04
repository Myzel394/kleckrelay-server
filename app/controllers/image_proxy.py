from uuid import UUID

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.models import ImageProxy
from app.utils import hash_fast, verify_fast_hash

__all__ = [
    "create_image_proxy",
    "find_image_by_url",
]


def create_image_proxy(
    db: Session,
    /,
    url: str,
) -> ImageProxy:
    image = ImageProxy(
        hashed_url=hash_fast(url),
    )

    db.add(image)
    db.commit()
    db.refresh(image)

    return image


def find_image_by_url(
    db: Session,
    /,
    url: str,
    id: str,
) -> ImageProxy:
    instance = db\
        .query(ImageProxy)\
        .filter(ImageProxy.id == UUID(id))\
        .one()

    if verify_fast_hash(instance.hashed_url, url):
        return instance

    raise NoResultFound()
