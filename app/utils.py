from functools import cache
from pathlib import Path

import email_normalize
from passlib.context import CryptContext

from typing import Iterator, TYPE_CHECKING

from sqlalchemy import inspect

if TYPE_CHECKING:
    from .database.base import Base

__all__ = [
    "normalize_email",
    "hash_slowly",
    "hash_fast",
    "verify_fast_hash",
    "verify_slow_hash",
    "contains_word",
]


pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


@cache
def _get_words() -> Iterator[str]:
    try:
        return (
            word.lower()
            for word in Path("/usr/share/dict/words")
                .read_text()
                .splitlines()
        )
    except OSError:
        return []


async def normalize_email(email: str) -> str:
    normalizer = email_normalize.Normalizer()

    return (await normalizer.normalize(email)).normalized_address


def hash_slowly(value: str) -> str:
    return pwd_context.hash(value)


def hash_fast(value: str) -> str:
    return pwd_context.hash(value)


def verify_fast_hash(hashed_value: str, value: str) -> bool:
    return pwd_context.verify(value, hashed_value)


def verify_slow_hash(hashed_value: str, value: str) -> bool:
    return pwd_context.verify(value, hashed_value)


def object_as_dict(obj: "Base") -> dict:
    return {
        attr.key: getattr(obj, attr.key)
        for attr in inspect(obj).mapper.column_attrs
    }


def contains_word(value: str) -> bool:
    return any(
        word in value
        for word in _get_words()
    )
