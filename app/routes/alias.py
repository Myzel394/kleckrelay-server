import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_pagination import Page, paginate, Params
from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from starlette.requests import Request

from app import logger
from app.controllers.alias import (
    create_alias, delete_alias, find_aliases_from_user_ordered, get_alias_from_user,
    update_alias,
)
from app.controllers.global_settings import get_filled_settings
from app.database.dependencies import get_db
from app.dependencies.get_instance_from_user import get_instance_from_user
from app.dependencies.get_user import get_user
from app.models import User
from app.models.alias import AliasType, EmailAlias
from app.schemas._basic import HTTPNotFoundExceptionModel, SimpleDetailResponseModel
from app.schemas.alias import AliasCreate, AliasDetail, AliasList, AliasUpdate
from app.controllers import global_settings as settings

router = APIRouter()


@router.get(
    "/",
    response_model=Page[AliasList]
)
def get_all_aliases(
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
    params: Params = Depends(),
    query: str = Query(""),
    active: bool = Query(None),
    alias_type: AliasType = Query(None),
):
    logger.info("Request: Get all aliases -> New Request.")

    return paginate(
        find_aliases_from_user_ordered(
            db,
            user=user,
            search=query,
            active=active,
            alias_type=alias_type,
        ),
        params
    )


@router.post(
    "/",
    response_model=AliasDetail,
)
async def create_alias_api(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_user),
):
    logger.info("Request: Create Alias -> New request. Validating data.")

    try:
        request_data = await request.json()
        alias_data = AliasCreate(settings=get_filled_settings(db), **request_data)
    except ValidationError as error:
        logger.info(f"Request: Create Alias -> Invalid data. {error.json()}")
        raise HTTPException(status_code=422, detail=error.errors())

    logger.info("Request: Create Alias -> Valid data. Creating alias.")

    alias = create_alias(db, alias_data, user)

    return alias


@router.patch(
    "/{id}",
    response_model=AliasDetail,
    responses={
        404: {
            "model": HTTPNotFoundExceptionModel
        }
    }
)
def update_alias_api(
    update: AliasUpdate,
    alias: EmailAlias = Depends(get_instance_from_user(get_alias_from_user)),
    db: Session = Depends(get_db),
):
    logger.info(f"Request: Update Alias -> Updating {alias=}.")
    update_alias(db, alias, update)
    logger.info(f"Request: Update Alias -> Updated successfully!")

    return alias


@router.get(
    "/{id}",
    response_model=AliasDetail,
    responses={
        403: {
            "model": SimpleDetailResponseModel,
            "description": "Maximum number of aliases reached."
        }
    }
)
def get_alias(
    alias: EmailAlias = Depends(get_instance_from_user(get_alias_from_user)),
):
    return alias


@router.delete(
    "/{id}",
    response_model=SimpleDetailResponseModel,
    responses={
        403: {
            "model": SimpleDetailResponseModel,
            "description": "Alias deletion is not allowed."
        },
        404: {
            "model": HTTPNotFoundExceptionModel,
            "description": "Alias not found."
        },
    }
)
def delete_alias_api(
    alias: EmailAlias = Depends(get_instance_from_user(get_alias_from_user)),
    db: Session = Depends(get_db),
):
    logger.info(f"Request: Delete Alias -> New request to delete {alias=}.")

    if not settings.get(db, "ALLOW_ALIAS_DELETION"):
        logger.info(f"Request: Delete Alias -> Alias deletion is not allowed.")
        raise HTTPException(
            status_code=403,
            detail="Alias deletion is not allowed."
        )

    logger.info(f"Request: Delete Alias -> Alias deletion is allowed. Deleting alias.")

    delete_alias(
        db,
        alias=alias,
    )
    logger.info(f"Request: Delete Alias -> Alias deleted successfully.")
    return {
        "detail": "Alias deleted successfully."
    }
