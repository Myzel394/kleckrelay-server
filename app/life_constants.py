import os
from pathlib import Path
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
    "API_DOMAIN",
    "MAIL_DOMAIN",
    "APP_DOMAIN",
    "RANDOM_EMAIL_ID_MIN_LENGTH",
    "RANDOM_EMAIL_ID_CHARS",
    "RANDOM_EMAIL_LENGTH_INCREASE_ON_PERCENTAGE",
    "CUSTOM_EMAIL_SUFFIX_LENGTH",
    "CUSTOM_EMAIL_SUFFIX_CHARS",
    "FROM_MAIL",
    "POSTFIX_HOST",
    "POSTFIX_PORT",
    "POSTFIX_USE_TLS",
    "DEBUG_MAILS",
    "SLOW_HASH_SALT",
    "FAST_HASH_SALT",
    "USER_PASSWORD_HASH_SALT",
    "EMAIL_LANDING_PAGE_URL_TEXT",
    "EMAIL_LANDING_PAGE_URL",
    "IMAGE_PROXY_TIMEOUT_IN_SECONDS",
    "IMAGE_PROXY_STORAGE_LIFE_TIME_IN_HOURS",
    "IMAGE_PROXY_STORAGE_PATH",
    "ENABLE_IMAGE_PROXY",
    "USER_EMAIL_ENABLE_DISPOSABLE_EMAILS",
    "USER_EMAIL_ENABLE_OTHER_RELAYS",
    "GNUPG_HOME_DIR",
    "SERVER_PRIVATE_KEY",
    "EMAIL_RESEND_WAIT_TIME_IN_SECONDS",
    "INSTANCE_SALT",
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


def get_float(name: str, default: Optional[str] = None) -> float:
    return float(_get_raw_value(name, default))


def get_str(name: str, default: Optional[str] = None) -> str:
    return _get_raw_value(name, default)


def get_path(name: str, default: Optional[str] = None, must_exist: bool = True) -> str:
    value = _get_raw_value(name, default)

    if value.startswith("~/"):
        value = Path.home() / value[2:]

    if must_exist and not os.path.exists(value):
        raise OSError(
            f"Doctor: Tried to get path {value} for constant {name}, but it does not exist. "
            f"Please create it or specify a different path."
        )


def get_list(name: str, default: list = None) -> list:
    default = default or []

    if (value := _get_raw_value(f"{name}_add", default="")) != "":
        return [
            *default,
            *value.split(",")
        ]

    return _get_raw_value(name).split(",")


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
API_DOMAIN = get_str("API_DOMAIN")
MAIL_DOMAIN = get_str("MAIL_DOMAIN")
APP_DOMAIN = get_str("APP_DOMAIN")
RANDOM_EMAIL_ID_MIN_LENGTH = get_int("RANDOM_EMAIL_ID_MIN_LENGTH")
RANDOM_EMAIL_ID_CHARS = get_str("RANDOM_EMAIL_ID_CHARS")
RANDOM_EMAIL_LENGTH_INCREASE_ON_PERCENTAGE = get_float("RANDOM_EMAIL_LENGTH_INCREASE_ON_PERCENTAGE")
CUSTOM_EMAIL_SUFFIX_LENGTH = get_int("CUSTOM_EMAIL_SUFFIX_LENGTH")
CUSTOM_EMAIL_SUFFIX_CHARS = get_str("CUSTOM_EMAIL_SUFFIX_CHARS")
FROM_MAIL = get_str("FROM_MAIL", default=f"noreply@{MAIL_DOMAIN}")
POSTFIX_HOST = get_str("POSTFIX_HOST")
POSTFIX_PORT = get_int("POSTFIX_PORT")
POSTFIX_USE_TLS = get_bool("POSTFIX_USE_TLS")
DEBUG_MAILS = get_bool("DEBUG_MAILS")
SLOW_HASH_SALT = get_str("SLOW_HASH_SALT")
FAST_HASH_SALT = get_str("FAST_HASH_SALT")
USER_PASSWORD_HASH_SALT = get_str("USER_PASSWORD_HASH_SALT")
EMAIL_LANDING_PAGE_URL_TEXT = get_str("EMAIL_LANDING_PAGE_URL_TEXT")
EMAIL_LANDING_PAGE_URL = get_str("EMAIL_LANDING_PAGE_URL")
IMAGE_PROXY_TIMEOUT_IN_SECONDS = get_int("IMAGE_PROXY_TIMEOUT_IN_SECONDS")
IMAGE_PROXY_STORAGE_LIFE_TIME_IN_HOURS = get_int("IMAGE_PROXY_STORAGE_LIFE_TIME_IN_HOURS")
IMAGE_PROXY_STORAGE_PATH = get_str("IMAGE_PROXY_STORAGE_PATH")
# This only affects new mails. Existing mails will still be able to proxy their requests.
ENABLE_IMAGE_PROXY = get_bool("ENABLE_IMAGE_PROXY")
USER_EMAIL_ENABLE_DISPOSABLE_EMAILS = get_bool("USER_EMAIL_ENABLE_DISPOSABLE_EMAILS")
USER_EMAIL_ENABLE_OTHER_RELAYS = get_bool("USER_EMAIL_ENABLE_OTHER_RELAYS")
# Can be used to block certain domains.
USER_EMAIL_OTHER_RELAY_DOMAINS = get_list("USER_EMAIL_OTHER_RELAY_DOMAINS")
GNUPG_HOME_DIR = get_path("GNUPG_HOME_DIR")
SERVER_PRIVATE_KEY = get_str("SERVER_PRIVATE_KEY")
EMAIL_RESEND_WAIT_TIME_IN_SECONDS = get_int("EMAIL_RESEND_WAIT_TIME_IN_SECONDS")
INSTANCE_SALT = get_str("INSTANCE_SALT")
