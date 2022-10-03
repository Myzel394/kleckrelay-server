from mailbox import Message

from aiosmtpd.smtp import Envelope

from app import logger
from app.database.dependencies import with_db
from email_utils import status
from email_utils.errors import EmailHandlerError
from email_utils.send_mail import (
    send_error_mail, send_mail_from_outside_to_private_mail,
    send_mail_from_private_mail_to_destination,
)
from email_utils.utils import get_alias_email, get_local_email

__all__ = [
    "handle",
]


def handle(envelope: Envelope, message: Message) -> str:
    logger.info("Retrieving mail from database.")

    with with_db() as db:
        logger.info(f"Checking if FROM mail {envelope.mail_from} is locally saved.")

        if email := get_local_email(db, email=envelope.mail_from):
            # LOCALLY saved user wants to send a mail FROM its private mail TO the outside.
            logger.info(
                f"Mail {envelope.mail_from} is a locally saved user. Relaying mail to "
                f"destination {envelope.rcpt_tos[0]}."
            )

            try:
                send_mail_from_private_mail_to_destination(envelope, message, email)

                return status.E200
            except EmailHandlerError:
                send_error_mail(
                    mail=envelope.mail_from,
                    targeted_mail=envelope.rcpt_tos[0],
                    language=email.user.language,
                )

                return status.E501

        logger.info(
            f"Checking if DESTINATION mail {envelope.rcpt_tos[0]} is an alias mail."
        )

        if alias := get_alias_email(db, email=envelope.rcpt_tos[0]):
            # OUTSIDE user wants to send a mail TO a locally saved user's private mail.
            logger.info(
                f"Email {envelope.mail_from} is from outside and wants to send to alias "
                f"{alias.address}. "
                f"Relaying email to locally saved user {alias.user.email.address}."
            )
            try:
                send_mail_from_outside_to_private_mail(envelope, message, alias)

                return status.E200
            except EmailHandlerError:
                send_error_mail(
                    mail=envelope.mail_from,
                    targeted_mail=envelope.rcpt_tos[0],
                    language=email.user.language,
                )

                return status.E521

        logger.info(
            f"Mail {envelope.mail_from} is neither a locally saved user nor does it want to "
            f"send to one. Sending error mail back."
        )

        return status.E501

