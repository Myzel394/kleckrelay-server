import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from . import default_life_constants

# We should probably add a feature to "lock" environment variables or at least show the hash of
# non-admin constants to prevent changes.

__all__ = [
    "DB_URI",
    "MAX_ENCRYPTED_NOTES_SIZE",
    "ACCESS_TOKEN_EXPIRE_IN_MINUTES",
    "REFRESH_TOKEN_EXPIRE_IN_MINUTES",
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
    "IMAGE_PROXY_TIMEOUT_IN_SECONDS",
    "IMAGE_PROXY_STORAGE_LIFE_TIME_IN_HOURS",
    "IMAGE_PROXY_STORAGE_PATH",
    "ENABLE_IMAGE_PROXY",
    "ENABLE_IMAGE_PROXY_STORAGE",
    "USER_EMAIL_ENABLE_DISPOSABLE_EMAILS",
    "USER_EMAIL_ENABLE_OTHER_RELAYS",
    "GNUPG_HOME_DIR",
    "SERVER_PRIVATE_KEY",
    "EMAIL_RESEND_WAIT_TIME_IN_SECONDS",
    "ALLOW_STATISTICS",
    "ADMINS",
    "DKIM_PRIVATE_KEY",
    "USER_EMAIL_OTHER_RELAY_DOMAINS",
    "MAX_ALIASES_PER_USER",
    "NON_VERIFIED_USER_LIFE_TIME_IN_DAYS",
    "ALLOW_LOGS",
    "ALLOW_ALIAS_DELETION",
    "USE_GLOBAL_SETTINGS",
    "KEEP_CRON_JOBS_AMOUNT",
    "SUPPORT_MAIL_FROM_NAME",
    "KDF_ITERATIONS",
    "KLECK_SECRET",
    "VERP_HMAC_ALGORITHM",
    "OTP_MAX_TRIES",
    "RECOVERY_CODE_CHARS",
    "RECOVERY_CODE_LENGTH",
    "IMAGE_PROXY_HMAC_ALGORITHM",
    "IMAGE_PROXY_FALLBACK_IMAGE_TYPE",
    "IMAGE_PROXY_FALLBACK_USER_AGENT_TYPE",
    "EMAIL_HANDLER_HOST",
    "RECOVERY_CODES_AMOUNT",
]

load_dotenv()


def _get_raw_value(name: str, default: Optional[str] = None) -> str:
    if (value := os.getenv(name)) is not None:
        return value

    if default is not None:
        return default

    return default_life_constants.__dict__.get(name, None)


def get_bool(name: str, default: Optional[str] = None) -> bool:
    return _get_raw_value(name, default).lower() in {"true", "1", "yes", "t", "y"}


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
IMAGE_PROXY_TIMEOUT_IN_SECONDS = get_int("IMAGE_PROXY_TIMEOUT_IN_SECONDS")
IMAGE_PROXY_STORAGE_LIFE_TIME_IN_HOURS = get_int("IMAGE_PROXY_STORAGE_LIFE_TIME_IN_HOURS")
IMAGE_PROXY_STORAGE_PATH = get_str("IMAGE_PROXY_STORAGE_PATH")
# This only affects new mails. Existing mails will still be able to proxy their requests.
ENABLE_IMAGE_PROXY = get_bool("ENABLE_IMAGE_PROXY")
ENABLE_IMAGE_PROXY_STORAGE = get_bool("ENABLE_IMAGE_PROXY_STORAGE")
USER_EMAIL_ENABLE_DISPOSABLE_EMAILS = get_bool("USER_EMAIL_ENABLE_DISPOSABLE_EMAILS")
USER_EMAIL_ENABLE_OTHER_RELAYS = get_bool("USER_EMAIL_ENABLE_OTHER_RELAYS")
# Can be used to block certain domains.
USER_EMAIL_OTHER_RELAY_DOMAINS = get_list("USER_EMAIL_OTHER_RELAY_DOMAINS")
GNUPG_HOME_DIR = get_path("GNUPG_HOME_DIR")
SERVER_PRIVATE_KEY = get_str("SERVER_PRIVATE_KEY")
EMAIL_RESEND_WAIT_TIME_IN_SECONDS = get_int("EMAIL_RESEND_WAIT_TIME_IN_SECONDS")
ALLOW_STATISTICS = get_bool("ALLOW_STATISTICS")
ADMINS = [value.lower() for value in get_list("ADMINS")]
USE_GLOBAL_SETTINGS = get_bool("USE_GLOBAL_SETTINGS")
DKIM_PRIVATE_KEY = get_str("DKIM_PRIVATE_KEY")
ALLOW_LOGS = get_bool("ALLOW_LOGS")
ALLOW_ALIAS_DELETION = get_bool("ALLOW_ALIAS_DELETION")
MAX_ALIASES_PER_USER = get_int("MAX_ALIASES_PER_USER")
NON_VERIFIED_USER_LIFE_TIME_IN_DAYS = get_int("NON_VERIFIED_USER_LIFE_TIME_IN_DAYS")
KEEP_CRON_JOBS_AMOUNT = get_int("KEEP_CRON_JOBS_AMOUNT")
SUPPORT_MAIL_FROM_NAME = get_str("SUPPORT_MAIL_FROM_NAME")
KLECK_SECRET = get_str("KLECK_SECRET")
KDF_ITERATIONS = get_int("KDF_ITERATIONS")
VERP_HMAC_ALGORITHM = get_str("VERP_HMAC_ALGORITHM")
OTP_MAX_TRIES = get_int("OTP_MAX_TRIES")
RECOVERY_CODE_CHARS = get_str("RECOVERY_CODE_CHARS")
RECOVERY_CODE_LENGTH = get_int("RECOVERY_CODE_LENGTH")
RECOVERY_CODES_AMOUNT = get_int("RECOVERY_CODES_AMOUNT")
IMAGE_PROXY_HMAC_ALGORITHM = get_str("IMAGE_PROXY_HMAC_ALGORITHM")
IMAGE_PROXY_FALLBACK_IMAGE_TYPE = get_str("IMAGE_PROXY_FALLBACK_IMAGE_TYPE")
IMAGE_PROXY_FALLBACK_USER_AGENT_TYPE = get_str("IMAGE_PROXY_FALLBACK_USER_AGENT_TYPE")
EMAIL_HANDLER_HOST = get_str("EMAIL_HANDLER_HOST")
