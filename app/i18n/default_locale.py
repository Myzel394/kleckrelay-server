from app import life_constants
from app.models import LanguageType

__all__ = [
    "DEFAULT_LOCALE"
]


DEFAULT_LOCALE = LanguageType(life_constants.DEFAULT_LOCALE)
