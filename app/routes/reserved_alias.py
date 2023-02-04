from fastapi import APIRouter, Depends, HTTPException, Query, Security
from fastapi_jwt import JwtAuthorizationCredentials
from fastapi_pagination import Page, paginate, Params
from sqlalchemy.orm import Session

from app import logger
from app.authentication.handler import access_security
from app.controllers.alias_utils import check_if_alias_exists
from app.controllers.user import get_admin_user_by_id
from app.database.dependencies import get_db
from app.life_constants import MAIL_DOMAIN
from app.schemas._basic import SimpleDetailResponseModel
from app.schemas.reserved_alias import ReservedAliasCreate, ReservedAliasDetail, ReservedAliasUpdate
from app.controllers.reserved_alias import (
    create_reserved_alias, delete_reserved_alias,
    find_reserved_aliases_ordered, update_reserved_alias,
)

router = APIRouter()


@router.get(
    "/",
    response_model=Page[ReservedAliasDetail]
)
def get_reserved_aliases_api(
    credentials: JwtAuthorizationCredentials = Security(access_security),
    db: Session = Depends(get_db),
    params: Params = Depends(),
    query: str = Query(""),
):
    logger.info("Request: Get all reserved aliases -> New Request.")

    get_admin_user_by_id(db, credentials["id"])

    aliases = find_reserved_aliases_ordered(
        db,
        search=query,
    )
    logger.info(
        f"Request: Get all reserved aliases -> Found {len(aliases)} aliases. Returning them back."
    )

    return paginate(
        aliases,
        params
    )


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
    user = get_admin_user_by_id(db, credentials["id"])
    logger.info(f"Request: Create Reserved Alias -> User {user=} is an admin.")

    if check_if_alias_exists(db, local=alias_data.local, domain=MAIL_DOMAIN):
        logger.info(f"Request: Create Reserved Alias -> Alias {alias_data.local}@{MAIL_DOMAIN} "
                    f"already exists.")
        raise HTTPException(status_code=400, detail="Alias already exists.")

    alias = create_reserved_alias(db, alias_data)

    logger.info(f"Request: Create Reserved Alias -> Alias created successfully! Returning "
                f"{alias=}.")
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
