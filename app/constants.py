import os.path
import string

from pathlib import Path

__all__ = [
    "LOCAL_REGEX",
    "DOMAIN_REGEX",
    "EMAIL_REGEX",
    "RELAY_LOCAL_REGEX",
    "RELAY_EMAIL_REGEX",
    "MAX_EMAIL_LENGTH",
    "MAX_LOCAL_LENGTH",
    "EMAIL_LOGIN_TOKEN_SAME_REQUEST_TOKEN_LENGTH",
    "EMAIL_LOGIN_TOKEN_SAME_REQUEST_TOKEN_CHARS",
    "EMAIL_VERIFICATION_TOKEN_CHARS",
    "EMAIL_VERIFICATION_TOKEN_LENGTH",
    "MAX_RANDOM_ALIAS_ID_GENERATION",
    "IS_TESTING",
    "PUBLIC_KEY_MAX_LENGTH",
    "ENCRYPTED_PRIVATE_KEY_MAX_LENGTH",
    "PUBLIC_KEY_MAX_LENGTH",
    "EMAIL_REPORT_ENCRYPTED_CONTENT_MAX_LENGTH",
    "ROOT_DIR",
]


# According to https://www.mailboxvalidator.com/resources/articles/acceptable-email-address-syntax-rfc/
LOCAL_REGEX = r"^[a-zA-Z0-9!\#\$\%\&\‘\*\+\–\/\=\?\^_\`\.\{\|\}\~.+-]{1,64}$"
DOMAIN_REGEX = r"^[a-zA-Z0-9-]{1,255}\.[a-zA-Z0-9-.]+$"
EMAIL_REGEX = f"^{LOCAL_REGEX[1:-1]}@{DOMAIN_REGEX[1:-1]}$"
RELAY_LOCAL_REGEX = r"^[a-zA-Z0-9!\#\$\%\&\‘\*\+\–\/\=\?\^_\`\.\{\|\}\~.+-]{1,68}$"
RELAY_EMAIL_REGEX = f"^{RELAY_LOCAL_REGEX[1:-1]}@{DOMAIN_REGEX[1:-1]}$"
MAX_EMAIL_LENGTH = 400
MAX_LOCAL_LENGTH = 64
EMAIL_LOGIN_TOKEN_SAME_REQUEST_TOKEN_LENGTH = 80
EMAIL_LOGIN_TOKEN_SAME_REQUEST_TOKEN_CHARS = string.ascii_letters + string.digits
EMAIL_VERIFICATION_TOKEN_CHARS = string.ascii_letters + string.digits
EMAIL_VERIFICATION_TOKEN_LENGTH = 80
# How often should be tried to generate a new alias id. After this amount, the length of the
# alias increases by one. This behavior continues until a new alias is found.
# This is an edge case scenario and will probably never occur.
MAX_RANDOM_ALIAS_ID_GENERATION = 200
IS_TESTING = False
PUBLIC_KEY_MAX_LENGTH = 10_000
ENCRYPTED_PRIVATE_KEY_MAX_LENGTH = 10_000
PUBLIC_KEY_REGEX = r"-----BEGIN PUBLIC KEY-----(\n|\r|\r\n)([0-9a-zA-Z\+\/=]{64}(\n|\r|\r\n))*([0-9a-zA-Z\+\/=]{1,63}(\n|\r|\r\n))?-----END PUBLIC KEY-----"
EMAIL_REPORT_ENCRYPTED_CONTENT_MAX_LENGTH = 200_000
ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent


TESTING_DB = None
