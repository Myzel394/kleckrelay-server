from starlette.requests import Request

from app.models import LanguageType, User

from .default_locale import DEFAULT_LOCALE

__all__ = [
    "get_language",
    "get_language_from_user",
]


def get_language(request: Request) -> LanguageType:
    """Return the language of the current request."""
    provided_language = request.headers.get("Accept-Language")

    if not provided_language:
        return DEFAULT_LOCALE

    # We currently only support English.
    match provided_language.lower():
        case "en-us" | "en" | "us" | "en_us":
            return LanguageType.EN_US
        case _:
            return DEFAULT_LOCALE


def get_language_from_user(user: User) -> LanguageType:
    """Return the language of the current user."""
    return user.language
