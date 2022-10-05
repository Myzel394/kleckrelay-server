import base64

import requests
from fastapi import APIRouter, Depends, HTTPException
from PIL import UnidentifiedImageError
from requests import HTTPError
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse
from urllib3.exceptions import ConnectTimeoutError

from app import life_constants, logger
from app.controllers.image_proxy import find_image_by_url
from app.database.dependencies import get_db
from app.helpers.parse_proxied_image import parse_proxied_image
from app.models import ImageProxyFormatType
from app.schemas._basic import HTTPBadRequestExceptionModel, HTTPNotFoundExceptionModel

router = APIRouter()


@router.get(
    "/{encoded_url}",
    responses={
        502: {
            "description": "Image could not be proxied / parsed.",
            "model": HTTPBadRequestExceptionModel,
        },
        404: {
            "description": "Upstream server returned a status of `404`.",
            "model": HTTPNotFoundExceptionModel,
        }
    }
)
def proxy_image(
    encoded_url: str,
    proxy_id: str,
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
        preferred_type = proxy_instance.email_alias.image_proxy_format

        logger.info(
            f"Request: Proxy Image -> Url {url=} found in database, but not cached. "
            f"Proxying image now..."
        )

        try:
            proxied_response = requests.request(
                method="GET",
                url=url,
                allow_redirects=True,
                timeout=life_constants.IMAGE_PROXY_TIMEOUT_IN_SECONDS,
            )
        except ConnectTimeoutError:
            logger.info(
                f"Request: Proxy Image -> Timeout while trying to proxy {url=}."
            )
            raise HTTPException(
                status_code=502,
                detail="Timeout while trying to proxy image.",
            )
        except HTTPError:
            logger.info(
                f"Request: Proxy Image -> Error while trying to proxy {url=}."
            )
            raise HTTPException(
                status_code=502,
                detail="Error while trying to proxy image.",
            )

        if proxied_response.status_code == 404:
            logger.info(
                f"Request: Proxy Image -> `404` Error while trying to proxy {url=}."
            )
            raise HTTPException(
                detail="Upstream server returned a status of `404`.",
                status_code=404,
            )

        if proxied_response.status_code != 200:
            logger.info(
                f"Request: Proxy Image -> {url=} did not return a status code of `200`."
            )
            raise HTTPException(
                detail={
                    "message": "Image could not be proxied.",
                    "original_status_code": proxied_response.status_code,
                },
                status_code=502,
            )

        image_bytes = None

        try:
            logger.info(
                f"Request: Proxy Image -> Trying to parse proxied image {url=}."
            )
            image_bytes = parse_proxied_image(
                content=proxied_response.content,
                preferred_type=preferred_type,
            )
        except UnidentifiedImageError:
            logger.info(
                f"Request: Proxy Image -> {url=} did not return a valid image."
            )

            if preferred_type != ImageProxyFormatType.JPEG:
                # Fallback to JPEG

                logger.info(
                    f"Request: Proxy Image -> Fallback to parse proxied image {url=} as a `JPEG`."
                )

                try:
                    image_bytes = parse_proxied_image(
                        content=proxied_response.content,
                        preferred_type=ImageProxyFormatType.JPEG,
                    )
                except UnidentifiedImageError:
                    pass

            if image_bytes is None:
                raise HTTPException(
                    detail="Image could not be parsed.",
                    status_code=502,
                )

        return StreamingResponse(
            image_bytes,
            media_type=f"image/{str(preferred_type).lower()}",
        )
