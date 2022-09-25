import base64
import string

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
]

DB_URI = "postgresql://user:password@127.0.0.1:35432/mail"
MAX_ENCRYPTED_NOTES_SIZE = 10_000
ACCESS_TOKEN_EXPIRE_IN_MINUTES = 10
REFRESH_TOKEN_EXPIRE_IN_MINUTES = 60 * 24 * 150  # 30 Days
# CHANGE THIS IN PRODUCTION!!!
JWT_SECRET_KEY = base64.b64decode("IyNNYWlsVGVzdF9TZWNyZXRLZXlfQ2hhbmdlX01l")
# CHANGE THIS IN PRODUCTION!!!
JWT_REFRESH_SECRET_KEY = base64.b64decode("IyNNYWlsVGVzdF9SZWZyZXNoX1NlY3JldEtleV9DaGFuZ2VfTWU=")
EMAIL_LOGIN_TOKEN_LENGTH = 5
EMAIL_LOGIN_TOKEN_CHARS = string.digits
EMAIL_LOGIN_TOKEN_MAX_TRIES = 5
EMAIL_LOGIN_TOKEN_EXPIRATION_IN_SECONDS = 60 * 15  # 15 minutes
EMAIL_LOGIN_TOKEN_CHECK_EMAIL_EXISTS = "True"
IS_DEBUG = "False"
DOMAIN = "kleckrelay.com"
MAIL_DOMAIN = "mail.kleckrelay.com"
RANDOM_EMAIL_ID_MIN_LENGTH = 6
RANDOM_EMAIL_ID_CHARS = string.ascii_letters + string.digits
CUSTOM_EMAIL_SUFFIX_LENGTH = 4
CUSTOM_EMAIL_SUFFIX_CHARS = string.digits