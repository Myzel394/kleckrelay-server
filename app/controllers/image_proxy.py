import uuid
from io import BytesIO
from uuid import UUID

import requests
from PIL import Image
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app import life_constants, logger
from app.constants import ROOT_DIR
from app.models import EmailAlias, ImageProxy
from app.utils.hashes import hash_fast, verify_fast_hash

__all__ = [
    "create_image_proxy",
    "find_image_by_url",
    "download_image_to_database"
]

from app.utils.download_image import download_image

STORAGE_PATH = ROOT_DIR / life_constants.IMAGE_PROXY_STORAGE_PATH


def create_image_proxy(
    db: Session,
    /,
    alias: EmailAlias,
    url: str,
) -> ImageProxy:
    image = ImageProxy(
        hashed_url=hash_fast(url),
        alias_id=alias.id,
    )

    db.add(image)
    db.commit()
    db.refresh(image)

    download_image_to_database(
        db,
        instance=image,
        url=url,
        user_agent=alias.get_user_agent_string(),
    )

    return image


def find_image_by_url(
    db: Session,
    /,
    url: str,
    id: uuid.UUID,
) -> ImageProxy:
    instance = db\
        .query(ImageProxy)\
        .filter_by(id=id)\
        .one()

    if verify_fast_hash(instance.hashed_url, url):
        return instance

    raise NoResultFound()


def download_image_to_database(
    db: Session,
    /,
    instance: ImageProxy,
    url: str,
    user_agent: str,
) -> None:
    logger.info(f"Download Image -> Downloading image for {url=}.")

    content = download_image(
        url=url,
        user_agent=user_agent,
        preferred_type=instance.email_alias.proxy_image_format,
    )

    with Image.open(content) as image:
        file = STORAGE_PATH / str(instance.alias_id) / f"{instance.id}.{image.format.lower()}"

        file.parent.mkdir(parents=True, exist_ok=True)
        file.touch(exist_ok=True)

        logger.info(f"Download Image -> Saving image {url=} to {file=}.")

        image.save(str(file))

    logger.info(f"Download Image -> Saving downloaded image {url=} to database.")
    instance.path = str(file.relative_to(ROOT_DIR / life_constants.IMAGE_PROXY_STORAGE_PATH))

    db.add(instance)
    db.commit()
    db.refresh(instance)
