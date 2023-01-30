from fastapi import APIRouter, Depends, Security
from fastapi_jwt import JwtAuthorizationCredentials
from sqlalchemy.orm import Session

from app import logger
from app.authentication.handler import access_security
from app.controllers.user import get_admin_user_by_id
from app.database.dependencies import get_db
from app.schemas._basic import SimpleDetailResponseModel
from app.schemas.reserved_alias import ReservedAliasCreate, ReservedAliasDetail, ReservedAliasUpdate
from app.controllers.reserved_alias import (
    create_reserved_alias, delete_reserved_alias,
    update_reserved_alias,
)

router = APIRouter()


@router.post(
    "/",
    response_model=ReservedAliasDetail
)
def create_reserved_alias_api(
    alias_data: ReservedAliasCreate,
    credentials: JwtAuthorizationCredentials = Security(access_security),
    db: Session = Depends(get_db),
):
    logger.info("Request: Create Reserved Alias -> New Request.")

    # Validate user being an admin
    get_admin_user_by_id(db, credentials["id"])

    alias = create_reserved_alias(db, alias_data)

    return alias


@router.patch(
    "/{id}",
    response_model=ReservedAliasDetail
)
def update_reserved_alias_api(
    id: str,
    alias_data: ReservedAliasUpdate,
    credentials: JwtAuthorizationCredentials = Security(access_security),
    db: Session = Depends(get_db),
):
    logger.info("Request: Update Reserved Alias -> New Request.")

    # Validate user being an admin
    get_admin_user_by_id(db, credentials["id"])

    alias = update_reserved_alias(db, id, alias_data)

    return alias


@router.delete(
    "/{id}",
    response_model=SimpleDetailResponseModel
)
def update_reserved_alias_api(
    id: str,
    credentials: JwtAuthorizationCredentials = Security(access_security),
    db: Session = Depends(get_db),
):
    logger.info("Request: Delete Reserved Alias -> New Request.")

    # Validate user being an admin
    get_admin_user_by_id(db, credentials["id"])

    delete_reserved_alias(db, id)

    return {
        "detail": "Alias deleted successfully."
    }
