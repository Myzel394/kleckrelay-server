import secrets
from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.constants import MAX_RANDOM_ALIAS_ID_GENERATION
from app.life_constants import (
    CUSTOM_EMAIL_SUFFIX_CHARS, CUSTOM_EMAIL_SUFFIX_LENGTH, RANDOM_EMAIL_ID_CHARS,
    RANDOM_EMAIL_ID_MIN_LENGTH, RANDOM_EMAIL_LENGTH_INCREASE_ON_PERCENTAGE,
)
from app.models import User
from app.models.alias import EmailAlias
from app.utils import contains_word

__all__ = [
    "generate_random_local_id",
    "create_local_with_suffix",
    "get_alias_from_user",
]


def get_aliases_amount(db: Session, /, domain: str) -> int:
    return db.query(EmailAlias.domain).filter(EmailAlias.domain == domain).count()


def generate_id(length: int = RANDOM_EMAIL_ID_MIN_LENGTH) -> str:
    while True:
        alias_id = "".join(
            secrets.choice(RANDOM_EMAIL_ID_CHARS)
            for _ in range(length)
        )

        if not contains_word(alias_id):
            return alias_id


def generate_suffix(length: int = CUSTOM_EMAIL_SUFFIX_LENGTH) -> str:
    return "".join(
        secrets.choice(CUSTOM_EMAIL_SUFFIX_CHARS)
        for _ in range(length)
    )


def check_if_local_exists(db: Session, /, local: str, domain: str) -> bool:
    return db.query(db
        .query(EmailAlias)
        .filter(EmailAlias.domain == domain)
        .filter(EmailAlias.local == local)
        .exists()
    ).scalar()


def calculate_id_length(aliases_amount: int) -> int:
    """Calculates the required min length for a new alias."""
    if aliases_amount <= 1:
        return RANDOM_EMAIL_ID_MIN_LENGTH

    length = RANDOM_EMAIL_ID_MIN_LENGTH

    while True:
        amount = aliases_amount / (len(RANDOM_EMAIL_ID_CHARS) ** length)

        if amount <= RANDOM_EMAIL_LENGTH_INCREASE_ON_PERCENTAGE:
            return length

        length += 1


def generate_random_local_id(db: Session, /, domain: str) -> str:
    generation_round = 1
    amount = get_aliases_amount(db, domain=domain)
    length = calculate_id_length(aliases_amount=amount)

    while True:
        alias_id = generate_id(length)

        if not check_if_local_exists(db, local=alias_id, domain=domain):
            return alias_id

        generation_round += 1

        if generation_round > MAX_RANDOM_ALIAS_ID_GENERATION:
            length += 1


def create_local_with_suffix(db: Session, /, local: str, domain: str) -> str:
    while True:
        suffix = generate_suffix()

        suggested_local = f"{local}.{suffix}"

        if not check_if_local_exists(db, local=suggested_local, domain=domain):
            return suggested_local


def get_alias_from_user(db: Session, /, user: User, id: str) -> Optional[EmailAlias]:
    return db\
        .query(EmailAlias)\
        .filter(and_(EmailAlias.user == user, EmailAlias.id == id))\
        .one()

