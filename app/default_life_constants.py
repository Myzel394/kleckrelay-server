import base64
import string

DB_URI = "postgresql://user:password@127.0.0.1:35432/mail"
MAX_ENCRYPTED_NOTES_SIZE = 10_000
ACCESS_TOKEN_EXPIRE_IN_MINUTES = 60 * 3  # 3 hours
REFRESH_TOKEN_EXPIRE_IN_MINUTES = 60 * 24 * 60  # 60 Days
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
APP_DOMAIN = "app.kleckrelay.com"
RANDOM_EMAIL_ID_MIN_LENGTH = 6
RANDOM_EMAIL_ID_CHARS = string.ascii_letters + string.digits
RANDOM_EMAIL_LENGTH_INCREASE_ON_PERCENTAGE = 0.4
CUSTOM_EMAIL_SUFFIX_LENGTH = 4
CUSTOM_EMAIL_SUFFIX_CHARS = string.digits
POSTFIX_HOST = "127.0.0.1"
POSTFIX_PORT = 25
POSTFIX_USE_TLS = "True"
DEBUG_MAILS = "False"
SLOW_HASH_SALT = "KleckRelay_#ChangeMe"
FAST_HASH_SALT = "KleckRelay_#ChangeMeToo"
USER_PASSWORD_HASH_SALT = "KleckRelay_#AlsoChangeMeToo"
EMAIL_LANDING_PAGE_URL_TEXT = "KleckRelay"
EMAIL_LANDING_PAGE_URL = "kleckrelay.com"
IMAGE_PROXY_TIMEOUT_IN_SECONDS = 8
IMAGE_PROXY_STORAGE_LIFE_TIME_IN_HOURS = 24
IMAGE_PROXY_STORAGE_PATH = "./storage/image_proxy/images"
ENABLE_IMAGE_PROXY = "True"
USER_EMAIL_ENABLE_DISPOSABLE_EMAILS = "False"
USER_EMAIL_ENABLE_OTHER_RELAYS = "True"
USER_EMAIL_OTHER_RELAY_DOMAINS = ",".join({
    "duck.com",

    "simplelogin.com",
    "aleeas.com",
    "slmail.me",
    "simplelogin.fr",

    "mozmail.com",

    "anonaddy.com",
    "anonaddy.me"
})
GNUPG_HOME_DIR = "/usr/bin/gpg"
