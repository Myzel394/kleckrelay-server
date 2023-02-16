import base64
import uuid

from fastapi import APIRouter, Depends
from PIL import UnidentifiedImageError
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from app import logger
from app.controllers.image_proxy import download_image_to_database, find_image_by_url
from app.database.dependencies import get_db
from app.utils.parse_proxied_image import convert_image_to_type
from app.schemas._basic import HTTPBadRequestExceptionModel, HTTPNotFoundExceptionModel
from app.utils import download_image

router = APIRouter()


@router.get(
    "/{encoded_url}",
    responses={
        502: {
            "description": "Image could not be proxied / parsed.",
            "model": HTTPBadRequestExceptionModel,
        },
        404: {
            "description": "Upstream Server returned a status of `404`.",
            "model": HTTPNotFoundExceptionModel,
        }
    }
)
def proxy_image(
    encoded_url: str,
    proxy_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    logger.info("Request: Proxy Image -> New request")
    url = base64.b64decode(encoded_url).decode("utf-8")
    logger.info(f"Request: Proxy Image -> {url=} should be proxied.")

    try:
        logger.info(f"Request: Proxy Image -> Trying to find {url=} in database.")
        proxy_instance = find_image_by_url(db, url, id=proxy_id)
    except NoResultFound as error:
        logger.info(f"Request: Proxy Image -> {url=} not found.")
        return {}
    else:
        logger.info(
            f"Request: Proxy Image -> Url {url=} found in database."
        )

        if proxy_instance.should_download():
            logger.info(
                f"Request: Proxy Image -> Url {url=} should be cached. Downloading image now..."
            )

            download_image_to_database(
                db,
                instance=proxy_instance,
                url=url,
                user_agent=proxy_instance.email_alias.get_user_agent_string(),
            )

        if proxy_instance.is_available():
            logger.info(
                f"Request: Proxy Image -> Url {url=} is cached. Returning cache."
            )

            try:
                return StreamingResponse(
                    convert_image_to_type(
                        proxy_instance.absolute_path.read_bytes(),
                        preferred_type=proxy_instance.email_alias.proxy_image_format,
                    ),
                    media_type=f"image/{str(proxy_instance.email_alias.proxy_image_format).lower()}",
                )
            except (UnidentifiedImageError, ValueError, IOError):
                logger.info(
                    f"Request: Proxy Image -> There was an error while trying to return image "
                    f"{url=}. We will try to proxy it now."
                )

        logger.info(
            f"Request: Proxy Image -> Proxying image {url=} now."
        )

        return StreamingResponse(
            download_image(
                url=url,
                preferred_type=proxy_instance.email_alias.proxy_image_format,
                user_agent=proxy_instance.email_alias.get_user_agent_string(),
            ),
            media_type=f"image/{str(proxy_instance.email_alias.proxy_image_format).lower()}",
        )
