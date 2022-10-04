import base64
from io import BytesIO, StringIO

import requests
from fastapi import APIRouter, Depends
from fastapi.openapi.models import Response
from PIL import Image
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from starlette.responses import FileResponse, StreamingResponse

from app.controllers.image_proxy import find_image_by_url
from app.database.dependencies import get_db
from app.models import ImageProxy
from app.utils import hash_fast

router = APIRouter()


@router.get("/{encoded_url}")
def proxy_image(
    encoded_url: str,
    proxy_id: str,
    db: Session = Depends(get_db),
):
    url = base64.b64decode(encoded_url).decode("utf-8")

    try:
        proxy_instance = find_image_by_url(db, url, id=proxy_id)
    except NoResultFound as error:
        return {}
    else:
        print("####" * 15)
        print(url)
        proxied_response = requests.request(
            method="GET",
            url="https://images.unsplash.com/photo-1663447000721-93a6d5bc71db?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2232&q=80",
            allow_redirects=True,
        )

        with BytesIO(proxied_response.content) as file:
            file.seek(0)

            return StreamingResponse(
                file.read(),
                status_code=proxied_response.status_code,
                media_type="image/jpg"
            )
