import re
from typing import Union

from aiosmtpd.smtp import Envelope

from app import constants
from app.models import EmailAlias
from app.utils.email import normalize_email
from email_utils.errors import AliasDisabledError, InvalidEmailError, PrivacyLeakError

__all__ = [
    "validate_envelope",
    "validate_alias",
    "check_for_email_privacy_leak",
]

FIND_EMAILS_REGEX = re.compile(constants.EMAIL_REGEX[1:-1], re.IGNORECASE)


def validate_email(email: str) -> None:
    if email == "<>":
        return

    if not re.match(constants.RELAY_EMAIL_REGEX, email):
        raise InvalidEmailError()


def validate_envelope(envelope: Envelope) -> None:
    # "<>" is required for bounce emails
    validate_email(envelope.mail_from)

    for mail in envelope.rcpt_tos:
        validate_email(mail)


def validate_alias(alias: Union[EmailAlias]) -> None:
    if not alias.is_active:
        raise AliasDisabledError()


async def check_for_email_privacy_leak(content: str, address: str) -> None:
    """Check if `address` is in `content` and raise an error if it is. `address` must be normalized.

    Works for normalized and non-normalized addresses.
    """

    # Search for all emails, normalize them and check if normalize email matches `address`
    for raw_email in FIND_EMAILS_REGEX.findall(content):
        normalized_email = await normalize_email(raw_email)

        if normalized_email == address:
            raise PrivacyLeakError(
                email=raw_email,
                normalized_email=normalized_email,
            )
