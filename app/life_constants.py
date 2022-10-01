import os
from typing import Optional

from . import default_life_constants

__all__ = [
    "DB_URI",
    "MAX_ENCRYPTED_NOTES_SIZE",
    "ACCESS_TOKEN_EXPIRE_IN_MINUTES",
    "REFRESH_TOKEN_EXPIRE_IN_MINUTES",
    "JWT_SECRET_KEY",
    "JWT_REFRESH_SECRET_KEY",
    "EMAIL_LOGIN_TOKEN_LENGTH",
    "EMAIL_LOGIN_TOKEN_CHARS",
    "EMAIL_LOGIN_TOKEN_MAX_TRIES",
    "EMAIL_LOGIN_TOKEN_EXPIRATION_IN_SECONDS",
    "EMAIL_LOGIN_TOKEN_CHECK_EMAIL_EXISTS",
    "IS_DEBUG",
    "DOMAIN",
    "MAIL_DOMAIN",
    "RANDOM_EMAIL_ID_MIN_LENGTH",
    "RANDOM_EMAIL_ID_CHARS",
    "CUSTOM_EMAIL_SUFFIX_LENGTH",
    "CUSTOM_EMAIL_SUFFIX_CHARS",
    "FROM_MAIL",
    "POSTFIX_HOST",
    "POSTFIX_PORT",
    "POSTFIX_USE_TLS",
    "DEBUG_EMAILS",
]


def _get_raw_value(name: str, default: Optional[str] = None) -> str:
    if (value := os.getenv(name)) is not None:
        return value

    if default is not None:
        return default

    return default_life_constants.__dict__.get(name, None)


def get_bool(name: str, default: Optional[str] = None) -> bool:
    return _get_raw_value(name, default).lower() in {"true", "1", "yes", "t"}


def get_int(name: str, default: Optional[str] = None) -> int:
    return int(_get_raw_value(name, default))


def get_str(name: str, default: Optional[str] = None) -> str:
    return _get_raw_value(name, default)


DB_URI = get_str("DB_URI")
MAX_ENCRYPTED_NOTES_SIZE = get_str("MAX_ENCRYPTED_NOTES_SIZE")
ACCESS_TOKEN_EXPIRE_IN_MINUTES = get_int("ACCESS_TOKEN_EXPIRE_IN_MINUTES")
REFRESH_TOKEN_EXPIRE_IN_MINUTES = get_int("REFRESH_TOKEN_EXPIRE_IN_MINUTES")
JWT_SECRET_KEY = get_str("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = get_str("JWT_REFRESH_SECRET_KEY")
EMAIL_LOGIN_TOKEN_LENGTH = get_int("EMAIL_LOGIN_TOKEN_LENGTH")
EMAIL_LOGIN_TOKEN_CHARS = get_str("EMAIL_LOGIN_TOKEN_CHARS")
EMAIL_LOGIN_TOKEN_MAX_TRIES = get_int("EMAIL_LOGIN_TOKEN_MAX_TRIES")
EMAIL_LOGIN_TOKEN_EXPIRATION_IN_SECONDS = get_int("EMAIL_LOGIN_TOKEN_EXPIRATION_IN_SECONDS")
EMAIL_LOGIN_TOKEN_CHECK_EMAIL_EXISTS = get_bool("EMAIL_LOGIN_TOKEN_CHECK_EMAIL_EXISTS")
IS_DEBUG = get_bool("IS_DEBUG")
DOMAIN = get_str("DOMAIN")
MAIL_DOMAIN = get_str("MAIL_DOMAIN")
RANDOM_EMAIL_ID_MIN_LENGTH = get_int("RANDOM_EMAIL_ID_MIN_LENGTH")
RANDOM_EMAIL_ID_CHARS = get_str("RANDOM_EMAIL_ID_CHARS")
CUSTOM_EMAIL_SUFFIX_LENGTH = get_int("CUSTOM_EMAIL_SUFFIX_LENGTH")
CUSTOM_EMAIL_SUFFIX_CHARS = get_str("CUSTOM_EMAIL_SUFFIX_CHARS")
FROM_MAIL = get_str("FROM_MAIL", default=f"noreply@{MAIL_DOMAIN}")
POSTFIX_HOST = get_str("POSTFIX_HOST")
POSTFIX_PORT = get_int("POSTFIX_PORT")
POSTFIX_USE_TLS = get_bool("POSTFIX_USE_TLS")
DEBUG_EMAILS = get_bool("DEBUG_EMAILS")
