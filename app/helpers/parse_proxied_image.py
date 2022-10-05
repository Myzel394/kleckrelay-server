from io import BytesIO

from PIL import Image

from app.models import ImageProxyFormatType

__all__ = [
    "parse_proxied_image"
]


def parse_proxied_image(
    content: bytes,
    preferred_type: ImageProxyFormatType,
) -> BytesIO:
    image_bytes = BytesIO(content)
    image = Image.open(image_bytes)

    if image.format.lower() != str(preferred_type).lower():
        image = Image.open(image_bytes)

        image.save(image_bytes, format=preferred_type)

    image_bytes.seek(0)

    return image_bytes
