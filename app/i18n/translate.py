from contextlib import contextmanager
from typing import Callable

import i18n
import string

from app.constants import ROOT_DIR
from app.models import LanguageType

__all__ = [
    "translate",
    "enter_translation",
]

ALLOWED_CHARACTERS = string.ascii_lowercase + "-_."


def _init_i18n() -> None:
    i18n.set("file_format", "json")
    i18n.set("enable_memoization", True)

    i18n.load_path.append(ROOT_DIR / "i18n" / "locales")

    locales = [
        language
        for language in LanguageType
    ]

    i18n.set("available_locales", locales)
    i18n.set("fallback", LanguageType.EN_US.value)


_init_i18n()


def translate(namespace: str, key: str, language: LanguageType) -> str:
    # Avoid hacking attacks like directory traversal.
    if not all(c in ALLOWED_CHARACTERS for c in key):
        raise ValueError(f"Invalid characters in key: {key}")

    return i18n.t(f"{namespace}.{key}", locale=language.value)


@contextmanager
def enter_translation(namespace: str, language: LanguageType) -> Callable:
    try:
        yield lambda key: translate(namespace, key, language)
    finally:
        pass
