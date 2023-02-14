import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_pagination import Page, paginate, Params
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app import logger
from app.controllers.alias_utils import check_if_alias_exists
from app.database.dependencies import get_db
from app.dependencies.get_user import get_admin_user
from app.life_constants import MAIL_DOMAIN
from app.models import User
from app.schemas._basic import SimpleDetailResponseModel
from app.schemas.reserved_alias import ReservedAliasCreate, ReservedAliasDetail, ReservedAliasUpdate
from app.controllers.reserved_alias import (
    create_reserved_alias, delete_reserved_alias_by_id,
    find_reserved_aliases_ordered, get_reserved_alias_by_id, update_reserved_alias,
)

router = APIRouter()


@router.get(
    "/",
    response_model=Page[ReservedAliasDetail]
)
def get_reserved_aliases_api(
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    params: Params = Depends(),
    query: str = Query(""),
):
    logger.info("Request: Get all reserved aliases -> New Request.")

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


@router.get(
    "/{id}",
    response_model=ReservedAliasDetail
)
def get_reserved_alias_api(
    id: uuid.UUID,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    logger.info("Request: Get Reserved Alias -> New Request.")

    try:
        alias = get_reserved_alias_by_id(db, id)
    except NoResultFound:
        logger.info(f"Request: Get Reserved Alias -> Alias {id} not found.")
        raise HTTPException(
            status_code=404,
            detail="Alias not found."
        )
    else:
        return alias


@router.post(
    "/",
    response_model=ReservedAliasDetail
)
def create_reserved_alias_api(
    alias_data: ReservedAliasCreate,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    logger.info("Request: Create Reserved Alias -> New Request.")

    if check_if_alias_exists(db, local=alias_data.local, domain=MAIL_DOMAIN):
        logger.info(
            f"Request: Create Reserved Alias -> "
            f"Alias {alias_data.local}@{MAIL_DOMAIN} already exists."
        )
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
    id: uuid.UUID,
    alias_data: ReservedAliasUpdate,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    logger.info("Request: Update Reserved Alias -> New Request.")

    alias = update_reserved_alias(db, id, alias_data)

    return alias


@router.delete(
    "/{id}",
    response_model=SimpleDetailResponseModel
)
def update_reserved_alias_api(
    id: uuid.UUID,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    logger.info("Request: Delete Reserved Alias -> New Request.")

    delete_reserved_alias_by_id(db, id)

    return {
        "detail": "Alias deleted successfully."
    }
