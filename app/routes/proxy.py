from fastapi import APIRouter, Depends, Query
from PIL import UnidentifiedImageError
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from app import life_constants
from app.controllers.alias import get_alias_by_id
from app.database.dependencies import get_db
from app.models.enums.alias import ImageProxyFormatType, ProxyUserAgentType
from app.schemas._basic import HTTPBadRequestExceptionModel
from app.utils.image import download_image, extract_image_data
from app.utils.parse_proxied_image import convert_image_to_type

router = APIRouter()

FALLBACK_TYPE = ImageProxyFormatType(life_constants.IMAGE_PROXY_FALLBACK_IMAGE_TYPE)
FALLBACK_USER_AGENT = ProxyUserAgentType(life_constants.IMAGE_PROXY_FALLBACK_USER_AGENT_TYPE)


@router.get("/image", responses={
    403: {
        "model": HTTPBadRequestExceptionModel,
        "description": "Invalid signature.",
    },
})
def proxy_image(
    db: Session = Depends(get_db),
    data: str = Query(..., description="The data of the request."),
    signature: str = Query(..., description="The signature of the request."),
):
    original_url, alias_id, image = extract_image_data(
        content=data,
        signature=signature,
    )

    preferred_format = FALLBACK_TYPE
    preferred_user_agent = FALLBACK_USER_AGENT

    try:
        alias = get_alias_by_id(db, id=alias_id)

        preferred_format = alias.proxy_image_format
        preferred_user_agent = alias.proxy_user_agent
    except NoResultFound:
        pass

    if image.exists():
        try:
            return StreamingResponse(
                convert_image_to_type(
                    image.read_bytes(),
                    preferred_type=preferred_format,
                ),
                media_type=f"image/{preferred_format.value.lower()}",
            )
        except (UnidentifiedImageError, ValueError, IOError):
            pass

    return StreamingResponse(
        download_image(
            url=original_url,
            preferred_type=preferred_format,
            user_agent=preferred_user_agent,
        ),
        media_type=f"image/{preferred_format.value.lower()}",
    )
