from mailbox import Message

from aiosmtpd.smtp import Envelope
from sqlalchemy.orm import Session

from app import life_constants, logger
from app.controllers.email_report import create_email_report_from_report_data
from app.database.dependencies import with_db
from app.email_report_data import EmailReportData
from app.models import LanguageType, User
from email_utils import status
from email_utils.errors import AliasNotFoundError, EmailHandlerError
from email_utils.html_handler import convert_images, remove_single_pixel_image_trackers
from email_utils.send_mail import (
    send_error_mail, send_mail,
)
from email_utils.utils import (
    generate_message_id, get_alias_by_email, get_header_unicode, get_local_email,
    parse_destination_email,
)
from email_utils.validators import validate_alias
from . import headers

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

        report = EmailReportData(
            mail_from=envelope.mail_from,
            mail_to=alias.address,
            subject=get_header_unicode(message[headers.SUBJECT]),
            message_id=message[headers.MESSAGE_ID],
        )

        if (content := message.get_payload()) is not None:
            if alias.remove_trackers:
                content = remove_single_pixel_image_trackers(report, html=content)

            if life_constants.ENABLE_IMAGE_PROXY and alias.proxy_images:
                content = convert_images(db, report, alias=alias, html=content)

            message.set_payload(content, "utf-8")

        if alias.create_mail_report and alias.user.public_key is not None:
            create_email_report_from_report_data(
                db,
                report_data=report,
                user=alias.user,
            )

        logger.info(
            f"Email {envelope.mail_from} is from outside and wants to send to alias "
            f"{alias.address}. "
            f"Relaying email to locally saved user {alias.user.email.address}."
        )

        return (
            alias.user.email.create_outside_email(envelope.mail_from),
            alias.user.email.address,
            alias.user
        )

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
            message[headers.MESSAGE_ID] = generate_message_id()
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
