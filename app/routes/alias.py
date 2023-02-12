from fastapi import APIRouter, Depends, HTTPException, Query, Security
from fastapi_jwt import JwtAuthorizationCredentials
from fastapi_pagination import Page, paginate, Params
from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from starlette.requests import Request

from app import constants, logger
from app.authentication.handler import access_security
from app.controllers.alias import (
    create_alias, find_aliases_from_user_ordered, get_alias_from_user,
    get_alias_from_user_by_address, update_alias,
)
from app.controllers.global_settings import get_filled_settings
from app.controllers.user import get_user_by_id
from app.database.dependencies import get_db
from app.models.alias import AliasType
from app.schemas._basic import HTTPNotFoundExceptionModel
from app.schemas.alias import AliasCreate, AliasDetail, AliasList, AliasUpdate

router = APIRouter()


@router.get(
    "/",
    response_model=Page[AliasList]
)
def get_all_aliases(
    credentials: JwtAuthorizationCredentials = Security(access_security),
    db: Session = Depends(get_db),
    params: Params = Depends(),
    query: str = Query(""),
    active: bool = Query(None),
    alias_type: AliasType = Query(None),
):
    logger.info("Request: Get all aliases -> New Request.")

    user = get_user_by_id(db, credentials["id"])

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
    credentials: JwtAuthorizationCredentials = Security(access_security),
    db: Session = Depends(get_db),
):
    logger.info("Request: Create Alias -> New request. Validating data.")

    try:
        request_data = await request.json()
        alias_data = AliasCreate(settings=get_filled_settings(db), **request_data)
    except ValidationError as error:
        logger.info(f"Request: Create Alias -> Invalid data. {error.json()}")
        raise HTTPException(status_code=422, detail=error.errors())

    logger.info("Request: Create Alias -> Valid data. Creating alias.")
    user = get_user_by_id(db, credentials["id"])

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
    id: str,
    update: AliasUpdate,
    credentials: JwtAuthorizationCredentials = Security(access_security),
    db: Session = Depends(get_db),
):
    logger.info(f"Request: Update Alias -> Updating alias with id={id}.")
    user = get_user_by_id(db, credentials["id"])

    try:
        alias = get_alias_from_user(db, user=user, id=id)
    except NoResultFound:
        logger.info(f"Request: Update Alias -> Alias {id} not found.")
        raise HTTPException(
            status_code=404,
            detail="Alias not found."
        )
    else:
        update_alias(db, alias, update)

        return alias


@router.get("/{id}", response_model=AliasDetail)
def get_alias(
    id: str,
    credentials: JwtAuthorizationCredentials = Security(access_security),
    db: Session = Depends(get_db),
):
    user = get_user_by_id(db, credentials["id"])

    try:
        alias = get_alias_from_user(
            db,
            user=user,
            id=id,
        )
    except NoResultFound:
        raise HTTPException(
            status_code=404,
            detail="Alias not found."
        )
    else:
        return alias
