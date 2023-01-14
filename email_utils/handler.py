from mailbox import Message

from aiosmtpd.smtp import Envelope
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app import life_constants, logger
from app.controllers.email_report import create_email_report_from_report_data
from app.database.dependencies import with_db
from app.email_report_data import EmailReportData
from app.models import LanguageType, User
from email_utils import status
from email_utils.errors import AliasNotFoundError, AliasNotYoursError, EmailHandlerError
from email_utils.html_handler import (
    convert_images, expand_shortened_urls,
    remove_single_pixel_image_trackers,
)
from email_utils.send_mail import (
    send_error_mail, send_mail,
)
from email_utils.utils import (
    get_alias_from_user, extract_alias_address, generate_message_id, get_alias_by_email,
    get_header_unicode,
    get_email_by_from,
)
from email_utils.validators import validate_alias
from . import headers
from .headers import set_header

__all__ = [
    "handle",
]


def handle(envelope: Envelope, message: Message) -> str:
    logger.info("Retrieving mail from database.")

    with with_db() as db:
        user = None

        try:
            set_header(message, headers.MESSAGE_ID, generate_message_id())

            logger.info(
                f"Checking if DESTINATION mail {envelope.rcpt_tos[0]} is a relay address."
            )

            if (result := extract_alias_address(envelope.rcpt_tos[0])) is not None:
                # LOCALLY saved user wants to send a mail FROM alias TO the outside.
                logger.info(
                    f"{envelope.rcpt_tos[0]} is an alias address. Checking if FROM user owns it."
                )

                alias, target = result

                try:
                    email = get_email_by_from(db, envelope.mail_from)
                except NoResultFound:
                    # Return "AliasNotYoursError" to avoid an alias being leaked
                    raise AliasNotYoursError()

                user = email.user

                try:
                    local_alias = get_alias_from_user(db, user, alias)
                except NoResultFound:
                    raise AliasNotYoursError()

                validate_alias(local_alias)

                logger.info(
                    f"Local mail {local_alias.address} should be relayed to outside mail {target}. "
                    f"Sending email now..."
                )

                send_mail(
                    message,
                    from_mail=local_alias.address,
                    to_mail=target,
                )

                return status.E200

            logger.info(
                f"Checking if DESTINATION mail {envelope.rcpt_tos[0]} is an alias mail."
            )

            if alias := get_alias_by_email(db, email=envelope.rcpt_tos[0]):
                user = alias.user

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

                    if alias.expand_url_shorteners:
                        content = expand_shortened_urls(report, alias=alias, html=content)

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

                send_mail(
                    message,
                    from_mail=alias.create_outside_email(envelope.mail_from),
                    from_name=envelope.mail_from,
                    to_mail=alias.user.email.address,
                )

                return status.E200

            logger.info(
                f"Mail {envelope.mail_from} is neither a locally saved user nor does it want to "
                f"send to one. Sending error mail back."
            )
            raise AliasNotFoundError(status_code=status.E515)
        except EmailHandlerError as error:
            send_error_mail(
                mail=envelope.mail_from,
                targeted_mail=envelope.rcpt_tos[0],
                error=error,
                language=user.language if user is not None else LanguageType.EN_US,
            )

            return error.status_code
