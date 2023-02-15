from functools import cache
from pathlib import Path
from typing import Iterator, TYPE_CHECKING

from sqlalchemy import inspect

if TYPE_CHECKING:
    from ..database.base import Base

__all__ = [
    "object_as_dict",
    "contains_word"
]


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
