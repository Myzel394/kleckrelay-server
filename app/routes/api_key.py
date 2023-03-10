import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app import logger
from app.controllers.api_key import create_api_key, delete_api_key, get_api_key_from_user_by_id
from app.database.dependencies import get_db
from app.dependencies.auth import AuthResult, get_auth
from app.schemas._basic import HTTPNotFoundExceptionModel, SimpleDetailResponseModel
from app.schemas.api_key import APIKeyCreatedResponseModel, APIKeyCreateModel

router = APIRouter()


@router.post("/", response_model=APIKeyCreatedResponseModel)
def create_api_key_api(
    data: APIKeyCreateModel,
    auth: AuthResult = Depends(get_auth()),
    db: Session = Depends(get_db),
):
    logger.info("Request: Create API Key -> New Request.")

    api_key_instance, key = create_api_key(db, user=auth.user, data=data)

    logger.info("Request: Create API Key -> Success! Returning back.")

    return {
        "id": api_key_instance.id,
        "key": key,
        "expires_at": api_key_instance.expires_at,
        "scopes": api_key_instance.scopes,
        "label": api_key_instance.label,
    }


@router.delete(
    "/{id}",
    response_model=SimpleDetailResponseModel,
    responses={
        404: {
            "model": HTTPNotFoundExceptionModel,
            "description": "API Key not found."
        },
    }
)
def delete_api_key_api(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(get_auth()),
):
    logger.info("Request: Delete API Key -> New Request.")

    try:
        api_key = get_api_key_from_user_by_id(db, user=auth.user, id=id)
    except NoResultFound:
        logger.info(f"Request: Delete API Key -> API Key with id={id} not found.")
        raise HTTPException(status_code=404, detail="API Key not found.")

    logger.info("Request: Delete API Key -> API Key found. Deleting API Key.")

    delete_api_key(db, api_key=api_key)

    logger.info("Request: Delete API Key -> API Key deleted. Returning back.")

    return {
        "detail": "API Key deleted successfully."
    }
