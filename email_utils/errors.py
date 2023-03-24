from dataclasses import dataclass

from email_utils import status

__all__ = [
    "EmailHandlerError",
    "InvalidEmailError",
    "AliasNotFoundError",
    "AliasDisabledError",
    "PrivacyLeakError",
]


class EmailHandlerError(Exception):
    status_code: str
    avoid_error_email: bool = False

    reason = "There is no specific reason given."


@dataclass
class InvalidEmailError(EmailHandlerError):
    status_code: str = status.E516

    reason = "The email you provided is invalid."


@dataclass
class AliasNotFoundError(EmailHandlerError):
    status_code: str = status.E502

    reason = "The alias you provided does not exist."


@dataclass
class AliasDisabledError(EmailHandlerError):
    status_code: str = status.E518

    reason = "The alias you provided has been disabled."


@dataclass
class AliasNotYoursError(EmailHandlerError):
    status_code: str = status.E502

    reason = "The alias you provided does not belong to you."


@dataclass
class PrivacyLeakError(EmailHandlerError):
    status_code: str = status.E501

    reason = "Your email contains leaked information."
