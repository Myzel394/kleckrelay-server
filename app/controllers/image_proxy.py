from sqlalchemy.orm import Session

from app.models import ImageProxy
from app.utils import hash_fast

__all__ = [
    "create_image_proxy",
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
