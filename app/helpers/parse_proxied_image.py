from io import BytesIO

from PIL import Image, UnidentifiedImageError

from app import logger

__all__ = [
    "convert_image_to_type"
]

from app.models.enums.alias import ImageProxyFormatType


def _convert(content: bytes, image_format: str) -> BytesIO:
    data = BytesIO(content)
    image = Image.open(data)

    if image.format.lower() != image_format:
        new_bytes = BytesIO()

        image.save(new_bytes, format=image_format)

        new_bytes.seek(0)

        return new_bytes
    else:
        data.seek(0)

        return data


def convert_image_to_type(
    content: bytes,
    preferred_type: ImageProxyFormatType,
    retry_with_jpeg_on_error: bool = True
) -> BytesIO:
    try:
        return _convert(content, str(preferred_type))
    except UnidentifiedImageError:
        if retry_with_jpeg_on_error and preferred_type != ImageProxyFormatType.JPEG:
            logger.info(
                f"Convert image to type: Error while trying to convert image to "
                f"{preferred_type=}. Falling back to JPEG now."
            )

            try:
                return _convert(content, str(ImageProxyFormatType.JPEG))
            except UnidentifiedImageError as error:
                raise error
