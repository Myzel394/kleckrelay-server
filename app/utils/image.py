import base64
import hmac
import json
import uuid
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode, urlunparse

import requests
from fastapi import HTTPException
from PIL import Image
from requests import HTTPError
from urllib3.exceptions import ConnectTimeoutError

from app import constant_keys, life_constants, logger
from app.constants import ROOT_DIR
from app.life_constants import IS_DEBUG
from app.models import EmailAlias
from app.models.constants.alias import PROXY_USER_AGENT_STRING_MAP
from app.utils.parse_proxied_image import convert_image_to_type
from app.models.enums.alias import ImageProxyFormatType, ProxyUserAgentType
from app.utils.url import Components

__all__ = [
    "create_image_url",
    "extract_image_data",
    "download_image",
    "save_image",
]

STORAGE_PATH = ROOT_DIR / "storage" / "proxy" / "images"


def _create_signature(payload: bytes) -> bytes:
    return hmac.new(
        constant_keys.IMAGE_PROXY_SECRET.encode("utf-8"),
        payload,
        life_constants.VERP_HMAC_ALGORITHM
    ).digest()


def create_image_url(
    original_url: str,
    alias_id: uuid.UUID,
    file: Optional[Path],
) -> str:
    raw_content = "_".join(
        (
            base64.b64encode(original_url.encode("utf-8")).decode("utf-8"),
            str(alias_id),
            str(file.relative_to(STORAGE_PATH)) if file else "",
            datetime.utcnow().isoformat(),
        )
    )

    proxy_url_content = base64.b64encode(raw_content.encode("utf-8"))
    proxy_url_signature = _create_signature(proxy_url_content)

    scheme = "https" if not IS_DEBUG else "http"
    url = urlunparse(
        Components(
            scheme=scheme,
            netloc=life_constants.API_DOMAIN,
            url="/v1/proxy/image",
            path="",
            query=urlencode({
                "data": proxy_url_content.decode("utf-8"),
                "signature": proxy_url_signature.hex(),
            }),
            fragment="",
        )
    )

    return url


def extract_image_data(
    content: str,
    signature: str,
) -> tuple[str, uuid.UUID, Path]:
    """Extract the data to a given image.

    Returns [original_url, alias_id, path]
    """
    expected_signature = _create_signature(content.encode("utf-8"))

    if expected_signature.hex() != signature:
        raise HTTPException(
            status_code=403,
            detail="Invalid Signature.",
        )

    original_url_in_base64, alias_id, relative_path, timestamp = base64\
        .b64decode(content)\
        .decode("utf-8")\
        .split("_")

    original_url = base64.b64decode(original_url_in_base64.encode("utf-8")).decode("utf-8")
    path = STORAGE_PATH / relative_path

    return original_url, uuid.UUID(alias_id), path


def download_image(
    url: str,
    preferred_type: ImageProxyFormatType,
    user_agent: ProxyUserAgentType,
) -> BytesIO:
    try:
        proxied_response = requests.request(
            method="GET",
            url=url,
            allow_redirects=True,
            timeout=life_constants.IMAGE_PROXY_TIMEOUT_IN_SECONDS,
            headers={
                "User-Agent": PROXY_USER_AGENT_STRING_MAP[user_agent],
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


def save_image(
    url: str,
    alias: EmailAlias,
) -> Path:
    content = download_image(
        url=url,
        user_agent=alias.proxy_user_agent,
        preferred_type=alias.proxy_image_format,
    )

    with Image.open(content) as image:
        file = (
            STORAGE_PATH /
            datetime.utcnow().strftime("%Y-%m-%d") /
            f"{uuid.uuid4()}.{image.format.lower()}"
        )

        file.parent.mkdir(parents=True, exist_ok=True)
        file.touch(exist_ok=True)

        logger.info(f"Download Image -> Saving image url={url} to {file=}.")

        image.save(str(file))

    return file
