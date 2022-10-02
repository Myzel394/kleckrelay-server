import re

from aiosmtpd.smtp import Envelope

from app import constants
from email_utils.errors import InvalidEmailError

__all__ = [
    "validate_envelope",
]


def validate_email(email: str) -> None:
    if not re.match(constants.RELAY_EMAIL_REGEX, email):
        raise InvalidEmailError(email)


def validate_envelope(envelope: Envelope) -> None:
    validate_email(envelope.mail_from)

    for mail in envelope.rcpt_tos:
        validate_email(mail)
