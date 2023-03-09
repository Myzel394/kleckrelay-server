from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import logger
from app.controllers.api_key import create_api_key
from app.database.dependencies import get_db
from app.dependencies.get_user import get_user
from app.models import User
from app.schemas.api_key import APIKeyCreatedResponseModel, APIKeyCreateModel

router = APIRouter()


@router.post("/", response_model=APIKeyCreatedResponseModel)
def create_api_key_api(
    data: APIKeyCreateModel,
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
):
    logger.info("Request: Create API Key -> New Request.")

    api_key_instance, key = create_api_key(db, user=user, data=data)

    logger.info("Request: Create API Key -> Success! Returning back.")

    return {
        "id": api_key_instance.id,
        "key": key,
        "expires_at": api_key_instance.expires_at,
        "scopes": api_key_instance.scopes,
    }
