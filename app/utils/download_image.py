from io import BytesIO

import requests
from fastapi import HTTPException
from requests import HTTPError
from urllib3.exceptions import ConnectTimeoutError

from app import life_constants, logger
from app.utils.parse_proxied_image import convert_image_to_type
from app.models.enums.alias import ImageProxyFormatType


def download_image(
    url: str,
    preferred_type: ImageProxyFormatType,
    user_agent: str,
) -> BytesIO:
    try:
        proxied_response = requests.request(
            method="GET",
            url=url,
            allow_redirects=True,
            timeout=life_constants.IMAGE_PROXY_TIMEOUT_IN_SECONDS,
            headers={
                "User-Agent": user_agent,
            }
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
            detail="Upstream Server returned a status of `404`.",
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

    return convert_image_to_type(
        proxied_response.content,
        preferred_type=preferred_type
    )
