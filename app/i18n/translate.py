import json
import string
from functools import cache
from typing import Any
from app import constants
from app.models import LanguageType

__all__ = [
    "translate",
]

ALLOWED_CHARACTERS = string.ascii_lowercase + "-_"


@cache
def _get_file(namespace: str, language: LanguageType) -> dict[str, Any]:
    content = constants.ROOT_DIR / "i18n" / language / f"{namespace}.json"

    return json.loads(content.read_text())


def translate(
    namespace: str,
    key: str,
    /,
    language: LanguageType
) -> str:
    """Return the translation for a given `key` in a given `namespace` for a given `language`.

    Supports keys like `foo.bar` to access nested keys.
    """
    if not all(char in ALLOWED_CHARACTERS for char in namespace):
        raise ValueError("Invalid namespace")

    content = _get_file(namespace, language)

    if "." in key:
        value = content

        for key in key.split("."):
            value = value[key]
    else:
        return content[key]
