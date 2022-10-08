from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi_jwt import JwtAuthorizationCredentials
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app import logger
from app.authentication.handler import access_security
from app.controllers.alias import (
    create_local_with_suffix, generate_random_local_id,
    get_alias_from_user,
)
from app.controllers.user import get_user_by_id
from app.database.dependencies import get_db
from app.life_constants import MAIL_DOMAIN
from app.models.alias import AliasType, EmailAlias
from app.schemas._basic import HTTPNotFoundExceptionModel
from app.schemas.alias import Alias, AliasCreate, AliasUpdate

router = APIRouter()


@router.get(
    "/",
    response_model=list[Alias]
)
def get_all_aliases(
    credentials: JwtAuthorizationCredentials = Security(access_security),
                                               db: Session = Depends(get_db),
):
    logger.info("Request: Get all aliases -> New Request.")

    user = get_user_by_id(db, credentials["id"])

    return user.email_aliases


@router.post(
    "/",
    response_model=Alias,
)
def create_alias(
    alias_data: AliasCreate,
    credentials: JwtAuthorizationCredentials = Security(access_security),
    db: Session = Depends(get_db),
):
    logger.info("Request: Create Alias -> Creating alias.")
    user = get_user_by_id(db, credentials["id"])

    if alias_data.type == AliasType.RANDOM:
        logger.info("Request: Create Alias -> Type is AliasType.RANDOM")
        local = generate_random_local_id(db, domain=MAIL_DOMAIN)
    else:
        logger.info("Request: Create Alias -> Type is AliasType.CUSTOM")
        local = create_local_with_suffix(db, domain=MAIL_DOMAIN, local=alias_data.local)

    logger.info(
        f"Request: Create Alias -> Creating email alias with local={local} and domain={MAIL_DOMAIN} "
        f"for {user.email.address}."
    )
    alias = EmailAlias(
        local=local,
        domain=MAIL_DOMAIN,
        is_active=alias_data.is_active,
        type=alias_data.type,
        user_id=user.id,
        pref_encrypted_notes=alias_data.encrypted_notes,

        pref_remove_trackers=alias_data.remove_trackers or user.preferences.alias_remove_trackers,
        pref_create_mail_report=alias_data.create_mail_report or user.preferences.alias_create_mail_report,
        pref_proxy_images=alias_data.proxy_images or user.preferences.alias_proxy_images,
        pref_image_proxy_user_agent=
            alias_data.image_proxy_user_agent or user.preferences.alias_image_proxy_user_agent,
    )

    logger.info("Request: Create Alias -> Saving instance.")
    db.add(alias)
    db.commit()
    db.refresh(alias)

    logger.info("Request: Create Alias -> Instance saved successfully.")
    return alias


@router.patch(
    "/{id}",
    response_model=Alias,
    responses={
        404: {
            "model": HTTPNotFoundExceptionModel
        }
    }
)
def update_alias(
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
        logger.info(f"Request: Update Alias -> Updating values of Alias {id}.")
        update_data = update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(alias, key, value)

        logger.info(f"Request: Update Alias -> Saving Alias {id} to database.")
        db.add(alias)
        db.commit()
        db.refresh(alias)

        logger.info(f"Request: Update Alias -> Alias {id} saved successfully.")
        return alias

