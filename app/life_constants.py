import os
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
]


def get_bool(name: str, default: str) -> bool:
    return os.getenv(name, default=default).lower() in {"true", "1", "yes", "t"}


DB_URI = os.getenv(
    "DB_URI",
    default=default_life_constants.DB_URI,
)
MAX_ENCRYPTED_NOTES_SIZE = os.getenv(
    "MAX_ENCRYPTED_NOTES_SIZE",
    default=default_life_constants.MAX_ENCRYPTED_NOTES_SIZE,
)
ACCESS_TOKEN_EXPIRE_IN_MINUTES = int(os.getenv(
    "ACCESS_TOKEN_EXPIRE_IN_MINUTES",
    default=default_life_constants.ACCESS_TOKEN_EXPIRE_IN_MINUTES,
))
REFRESH_TOKEN_EXPIRE_IN_MINUTES = int(os.getenv(
    "REFRESH_TOKEN_EXPIRE_IN_MINUTES",
    default=default_life_constants.REFRESH_TOKEN_EXPIRE_IN_MINUTES,
))
JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    default=default_life_constants.JWT_SECRET_KEY,
)
JWT_REFRESH_SECRET_KEY = os.getenv(
    "JWT_REFRESH_SECRET_KEY",
    default=default_life_constants.JWT_REFRESH_SECRET_KEY,
)
EMAIL_LOGIN_TOKEN_LENGTH = int(os.getenv(
    "EMAIL_LOGIN_TOKEN_LENGTH",
    default=default_life_constants.EMAIL_LOGIN_TOKEN_LENGTH,
))
EMAIL_LOGIN_TOKEN_CHARS = os.getenv(
    "EMAIL_LOGIN_TOKEN_CHARS",
    default=default_life_constants.EMAIL_LOGIN_TOKEN_CHARS,
)
EMAIL_LOGIN_TOKEN_MAX_TRIES = int(os.getenv(
    "EMAIL_LOGIN_TOKEN_MAX_TRIES",
    default=default_life_constants.EMAIL_LOGIN_TOKEN_MAX_TRIES,
))
EMAIL_LOGIN_TOKEN_EXPIRATION_IN_SECONDS = int(os.getenv(
    "EMAIL_LOGIN_TOKEN_EXPIRATION_IN_SECONDS",
    default=default_life_constants.EMAIL_LOGIN_TOKEN_EXPIRATION_IN_SECONDS,
))
EMAIL_LOGIN_TOKEN_CHECK_EMAIL_EXISTS = get_bool(
    "EMAIL_LOGIN_TOKEN_CHECK_EMAIL_EXISTS",
    default=default_life_constants.EMAIL_LOGIN_TOKEN_CHECK_EMAIL_EXISTS,
)
IS_DEBUG = get_bool(
    "IS_DEBUG",
    default=default_life_constants.IS_DEBUG,
)
DOMAIN = os.getenv(
    "DOMAIN",
    default=default_life_constants.DOMAIN,
)
