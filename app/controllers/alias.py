import secrets
from typing import Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.controllers import global_settings as settings
from app.constants import MAX_RANDOM_ALIAS_ID_GENERATION
from app.controllers.alias_utils import check_if_alias_exists, get_aliases_amount
from app.models import User
from app.models.alias import EmailAlias
from app.models.enums.alias import AliasType
from app.utils import contains_word

__all__ = [
    "get_alias_from_user",
    "get_alias_from_user_by_address",
    "find_aliases_from_user_ordered",
    "create_local_with_suffix",
    "generate_random_local_id"
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


def get_alias_from_user_by_address(
    db: Session,
    /,
    user: User,
    domain: str,
    local: str
) -> EmailAlias:
    return db \
        .query(EmailAlias) \
        .filter(and_(EmailAlias.user == user, EmailAlias.domain == domain, EmailAlias.local == local)) \
        .one()


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


def get_alias_from_user(db: Session, /, user: User, id: str) -> EmailAlias:
    return db \
        .query(EmailAlias) \
        .filter(and_(EmailAlias.user == user, EmailAlias.id == id)) \
        .one()


def generate_random_local_id(db: Session, /, domain: str = None) -> str:
    domain = domain or settings.get(db, "MAIL_DOMAIN")

    generation_round = 1
    amount = get_aliases_amount(db, domain=domain)
    length = _calculate_id_length(db, aliases_amount=amount)

    while True:
        alias_id = _generate_id(db, length)

        if not check_if_alias_exists(db, local=alias_id, domain=domain):
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

