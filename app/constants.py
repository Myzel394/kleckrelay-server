import string

__all__ = [
    "LOCAL_REGEX",
    "DOMAIN_REGEX",
    "EMAIL_REGEX",
    "PUBLIC_KEY_REGEX",
    "PRIVATE_KEY_REGEX",
    "MAX_EMAIL_LENGTH",
    "EMAIL_LOGIN_TOKEN_SAME_REQUEST_TOKEN_LENGTH",
    "EMAIL_LOGIN_TOKEN_SAME_REQUEST_TOKEN_CHARS",
    "ENCRYPTED_PASSWORD_LENGTH",
    "EMAIL_VERIFICATION_TOKEN_CHARS",
    "EMAIL_VERIFICATION_TOKEN_LENGTH",
]


# According to https://www.mailboxvalidator.com/resources/articles/acceptable-email-address-syntax-rfc/
LOCAL_REGEX = r"^[a-zA-Z0-9!\#\$\%\&\‘\*\+\–\/\=\?\^_\`\.\{\|\}\~.+-]{1,64}$"
DOMAIN_REGEX = r"^[a-zA-Z0-9-]{1,255}\.[a-zA-Z0-9-.]+$"
EMAIL_REGEX = f"^{LOCAL_REGEX[1:-1]}@{DOMAIN_REGEX[1:-1]}$"
PUBLIC_KEY_REGEX = r"-----BEGIN PUBLIC KEY-----(\n|\r|\r\n)([0-9a-zA-Z\+\/=]{64}(\n|\r|\r\n))*([0-9a-zA-Z\+\/=]{1,63}(\n|\r|\r\n))?-----END PUBLIC KEY-----"
PRIVATE_KEY_REGEX = r"-----BEGIN PRIVATE KEY-----(\n|\r|\r\n)([0-9a-zA-Z\+\/=]{64}(\n|\r|\r\n))*([0-9a-zA-Z\+\/=]{1,63}(\n|\r|\r\n))?-----END PRIVATE KEY-----"
MAX_EMAIL_LENGTH = 400
EMAIL_LOGIN_TOKEN_SAME_REQUEST_TOKEN_LENGTH = 80
EMAIL_LOGIN_TOKEN_SAME_REQUEST_TOKEN_CHARS = string.ascii_letters + string.digits
ENCRYPTED_PASSWORD_LENGTH = 2000
EMAIL_VERIFICATION_TOKEN_CHARS = string.ascii_letters + string.digits
EMAIL_VERIFICATION_TOKEN_LENGTH = 80
