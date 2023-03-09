import base64
import hmac
import uuid
from datetime import datetime
from urllib.parse import urlencode, urlunparse

from PIL import Image

from app import constant_keys, constants, life_constants, logger
from app.constants import ROOT_DIR
from app.life_constants import IS_DEBUG
from app.models import EmailAlias
from app.utils.image import download_image
from app.utils.url import Components

__all__ = [
    "create_image_proxy_url",
]


STORAGE_PATH = ROOT_DIR / "storage" / "proxy" / "images"


def _create_signature(payload: bytes) -> bytes:
    return hmac.new(
        constant_keys.IMAGE_PROXY_SECRET.encode("utf-8"),
        payload,
        constants.HMAC_ALGORITHM,
    ).digest()


def create_image_proxy_url(alias: EmailAlias, original_url: str) -> str:
    content = download_image(
        url=original_url,
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

        logger.info(f"Download Image -> Saving image url={original_url} to {file=}.")

        image.save(str(file))


    raw_content = original_url + "." + str(file.relative_to(STORAGE_PATH))
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
