from mailbox import Message

from aiosmtpd.smtp import Envelope
from sqlalchemy.orm import Session

from app import logger
from app.database.dependencies import with_db
from app.models import LanguageType, User
from email_utils import status
from email_utils.errors import AliasNotFoundError, EmailHandlerError
from email_utils.proxy_images import convert_images
from email_utils.send_mail import (
    send_error_mail, send_mail,
)
from email_utils.utils import (
    get_alias_by_email, get_local_email, parse_destination_email,
)
from email_utils.validators import validate_alias

__all__ = [
    "handle",
]


def _get_targets(db: Session, /, envelope: Envelope, message: Message) -> tuple[str, str, User]:
    """Returns [FROM, TO]."""

    logger.info(f"Checking if FROM mail {envelope.mail_from} is locally saved.")
    if email := get_local_email(db, email=envelope.mail_from):
        # LOCALLY saved user wants to send a mail FROM its private mail TO the outside.
        local_alias, forward_address = parse_destination_email(
            user=email.user,
            email=envelope.rcpt_tos[0],
        )

        validate_alias(local_alias)

        logger.info(
            f"Local mail {local_alias} should be relayed to outside mail {forward_address}. "
            f"Sending email now..."
        )

        return local_alias.address, forward_address, email.user

    logger.info(
        f"Checking if DESTINATION mail {envelope.rcpt_tos[0]} is an alias mail."
    )

    if alias := get_alias_by_email(db, email=envelope.rcpt_tos[0]):
        # OUTSIDE user wants to send a mail TO a locally saved user's private mail.
        validate_alias(alias)

        if alias.proxy_images:
            content = convert_images(db, message.as_string())

            message.set_payload(content, "utf-8")
        logger.info(
            f"Email {envelope.mail_from} is from outside and wants to send to alias "
            f"{alias.address}. "
            f"Relaying email to locally saved user {alias.user.email.address}."
        )

        return envelope.mail_from, alias.user.email.address, alias.user

    logger.info(
        f"Mail {envelope.mail_from} is neither a locally saved user nor does it want to "
        f"send to one. Sending error mail back."
    )
    raise AliasNotFoundError(status_code=status.E515)


def handle(envelope: Envelope, message: Message) -> str:
    logger.info("Retrieving mail from database.")

    with with_db() as db:
        user = None

        try:
            from_mail, to_mail, user = _get_targets(db, envelope, message)

            send_mail(
                from_mail=from_mail,
                to_mail=to_mail,
                message=message,
            )

            return status.E200
        except EmailHandlerError as error:
            send_error_mail(
                mail=envelope.mail_from,
                targeted_mail=envelope.rcpt_tos[0],
                error=error,
                language=user.language if user is not None else LanguageType.EN_US,
            )

            return error.status_code
