from dataclasses import dataclass

from email_utils import status

__all__ = [
    "EmailHandlerError",
    "InvalidEmailError",
    "AliasNotFoundError",
    "AliasDisabledError",
]


class EmailHandlerError(Exception):
    status_code: str
    avoid_error_email: bool = False


@dataclass
class InvalidEmailError(EmailHandlerError):
    status_code: str = status.E516


@dataclass
class AliasNotFoundError(EmailHandlerError):
    status_code: str = status.E502


@dataclass
class AliasDisabledError(EmailHandlerError):
    status_code: str = status.E518



@dataclass
class AliasNotYoursError(EmailHandlerError):
    status_code: str = status.E502
