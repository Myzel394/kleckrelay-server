import secrets
import uuid
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app import logger
from app.controllers import global_settings as settings
from app.constants import MAX_RANDOM_ALIAS_ID_GENERATION
from app.controllers.alias_utils import check_if_alias_exists, get_aliases_amount
from app.life_constants import MAIL_DOMAIN
from app.models import User
from app.models.alias import DeletedEmailAlias, EmailAlias
from app.models.enums.alias import AliasType
from app.schemas.alias import AliasCreate, AliasUpdate
from app.utils.common import contains_word

__all__ = [
    "get_alias_from_user",
    "find_aliases_from_user_ordered",
    "create_local_with_suffix",
    "generate_random_local_id",
    "create_alias",
    "update_alias",
    "delete_alias",
    "get_alias_by_id",
    "get_alias_by_local_and_domain",
]


def _calculate_id_length(db: Session, /, aliases_amount: int) -> int:
    """Calculates the required min length for a new alias."""
    length = settings.get(db, "RANDOM_EMAIL_ID_MIN_LENGTH")
    if aliases_amount <= 1:
        return length

    chars = settings.get(db, "RANDOM_EMAIL_ID_CHARS")
    percentage_change = settings.get(db, "RANDOM_EMAIL_LENGTH_INCREASE_ON_PERCENTAGE")

    while True:
        amount = aliases_amount / (len(chars) ** length)

        if amount <= percentage_change:
            return length

        length += 1


def _generate_id(db: Session, /, length: int) -> str:
    chars = settings.get(db, "RANDOM_EMAIL_ID_CHARS")

    while True:
        alias_id = "".join(
            secrets.choice(chars)
            for _ in range(length)
        )

        if not contains_word(alias_id):
            return alias_id


def _generate_suffix(db: Session, /) -> str:
    length = settings.get(db, "CUSTOM_EMAIL_SUFFIX_LENGTH")
    chars = settings.get(db, "CUSTOM_EMAIL_SUFFIX_CHARS")

    return "".join(
        secrets.choice(chars)
        for _ in range(length)
    )


def find_aliases_from_user_ordered(
    db: Session,
    /,
    user: User,
    search: str = "",
    active: Optional[bool] = None,
    alias_type: Optional[AliasType] = None,
):
    query = db \
        .query(EmailAlias) \
        .filter_by(user_id=user.id)

    if search:
        query = query.filter(
            func.similarity(EmailAlias.local, search) > 0.005
        )

    if active is not None:
        query = query.filter_by(is_active=active)

    if alias_type is not None:
        query = query.filter_by(type=alias_type)

    return query \
        .order_by(func.levenshtein(EmailAlias.local, search) if search else EmailAlias.local) \
        .all()


def get_alias_from_user(db: Session, /, user: User, id: uuid.UUID) -> EmailAlias:
    return db \
        .query(EmailAlias) \
        .filter(and_(EmailAlias.user == user, EmailAlias.id == id)) \
        .one()


def get_alias_by_id(db: Session, /, id: uuid.UUID) -> EmailAlias:
    return db \
        .query(EmailAlias) \
        .filter(EmailAlias.id == id) \
        .one()


def get_alias_by_local_and_domain(db: Session, /, local: str, domain: str) -> EmailAlias:
    return db \
        .query(EmailAlias) \
        .filter(and_(EmailAlias.local == local, EmailAlias.domain == domain)) \
        .one()


def generate_random_local_id(db: Session, /, domain: str = None) -> str:
    domain = domain or settings.get(db, "MAIL_DOMAIN")

    generation_round = 1
    amount = get_aliases_amount(db, domain=domain)
    length = _calculate_id_length(db, aliases_amount=amount)

    logger.info("Generate random local id -> Creating id...")

    while True:
        alias_id = _generate_id(db, length)

        if not check_if_alias_exists(db, local=alias_id, domain=domain):
            logger.info(f"Generate random local id -> Created id {alias_id}.")
            return alias_id

        generation_round += 1

        if generation_round > MAX_RANDOM_ALIAS_ID_GENERATION:
            length += 1


def create_local_with_suffix(db: Session, /, local: str, domain: str) -> str:
    while True:
        suffix = _generate_suffix(db)

        suggested_local = f"{local}.{suffix}"

        if not check_if_alias_exists(db, local=suggested_local, domain=domain):
            return suggested_local


def create_alias(db: Session, /, data: AliasCreate, user: User) -> EmailAlias:
    max_aliases_per_user = settings.get(db, "MAX_ALIASES_PER_USER")

    if max_aliases_per_user != 0:
        if len(user.email_aliases) >= max_aliases_per_user:
            raise HTTPException(
                status_code=403,
                detail="You have reached the maximum number of aliases."
            )

    if data.type == AliasType.RANDOM:
        logger.info("Request: Create Alias -> Type is AliasType.RANDOM")
        local = generate_random_local_id(db, domain=MAIL_DOMAIN)
    else:
        logger.info("Request: Create Alias -> Type is AliasType.CUSTOM")
        local = create_local_with_suffix(db, domain=MAIL_DOMAIN, local=data.local)

    logger.info(
        f"Request: Create Alias -> Creating email alias with local={local} and domain={MAIL_DOMAIN} "
        f"for {user.email.address}."
    )
    alias = EmailAlias(
        local=local,
        domain=MAIL_DOMAIN,
        is_active=data.is_active,
        type=data.type,
        user_id=user.id,
        encrypted_notes=data.encrypted_notes,

        pref_remove_trackers=data.pref_remove_trackers,
        pref_create_mail_report=data.pref_create_mail_report,
        pref_proxy_images=data.pref_proxy_images,
        pref_proxy_user_agent=data.pref_proxy_user_agent,
        pref_image_proxy_format=data.pref_image_proxy_format,
        pref_expand_url_shorteners=data.pref_expand_url_shorteners,
    )

    logger.info("Request: Create Alias -> Saving instance.")
    db.add(alias)
    db.commit()
    db.refresh(alias)
    logger.info("Request: Create Alias -> Instance saved successfully.")

    return alias


def update_alias(db: Session, /, alias: EmailAlias, data: AliasUpdate) -> None:
    logger.info(f"Request: Update Alias -> Updating values of Alias {alias.id}.")
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(alias, key, value)

    logger.info(f"Request: Update Alias -> Saving Alias {alias.id} to database.")
    db.add(alias)
    db.commit()
    db.refresh(alias)

    logger.info(f"Request: Update Alias -> Alias {alias.id} saved successfully.")


def delete_alias(db: Session, /, alias: EmailAlias) -> None:
    logger.info(f"Request: Delete Alias -> Deleting Alias {alias.id}.")

    logger.info("Request: Delete Alias -> Creating DeletedEmailAlias.")

    deleted_alias = DeletedEmailAlias(
        email=alias.address,
    )

    logger.info("Request: Delete Alias -> Saving DeletedEmailAlias.")
    db.add(deleted_alias)
    db.commit()
    db.refresh(deleted_alias)

    logger.info("Request: Delete Alias -> Deleting Alias.")

    db.delete(alias)
    db.commit()

    logger.info(f"Request: Delete Alias -> Alias {alias.id} deleted successfully.")
