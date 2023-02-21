import re
from typing import Union

from aiosmtpd.smtp import Envelope

from app import constants
from app.models import EmailAlias
from email_utils.errors import AliasDisabledError, InvalidEmailError

__all__ = [
    "validate_envelope",
    "validate_alias",
]


def validate_email(email: str) -> None:
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
