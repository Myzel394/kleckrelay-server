import logging

import binascii
from mailbox import Message
from typing import Union

from aiosmtpd.smtp import Envelope
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from sqlalchemy.sql import Alias

from app import life_constants, logger
from app.controllers.alias import get_alias_by_local_and_domain
from app.controllers import server_statistics
from app.controllers.reserved_alias import get_reserved_alias_by_address
from app.database.dependencies import with_db
from app.models import ReservedAlias
from email_utils import status
from email_utils.errors import AliasNotFoundError, EmailHandlerError
from email_utils.send_mail import (
    draft_message, send_mail,
)
from email_utils.utils import (
    extract_alias_address, generate_message_id
)
from email_utils.validators import validate_alias
from . import headers
from .bounce_messages import (
    extract_forward_status, extract_forward_status_header, extract_in_reply_to_header,
    generate_forward_status,
    get_report_from_message, is_not_deliverable, StatusType,
)
from .handle_local_to_outside import handle_local_to_outside
from .handle_outside_to_local import handle_outside_to_local
from .headers import set_header

__all__ = [
    "handle",
]


def get_alias(db: Session, /, local: str, domain: str) -> Union[Alias, ReservedAlias, None]:
    # Try reserved alias
    try:
        return get_reserved_alias_by_address(db, local=local, domain=domain)
    except NoResultFound:
        pass


async def handle(envelope: Envelope, message: Message) -> str:
    logger.info("Retrieving mail from database.")

    with with_db() as db:
        try:
            original_message_id = message[headers.MESSAGE_ID] or ""
            message_id = generate_message_id()
            set_header(message, headers.MESSAGE_ID, message_id)

            logger.info("Checking if mail is a bounce mail from us.")
            if (report_message := get_report_from_message(message)) is not None:
                if (forward_status := extract_forward_status_header(report_message)) is not None:
                    logger.info("Mail is a bounce mail from us. Extracting data.")

                    try:
                        data = extract_forward_status(forward_status)
                    except (ValueError, binascii.Error):
                        logger.info("Forward status is invalid. Ignoring mail.")
                        return status.E200

                    logger.info(f"Data is {data=}.")

                    if data["status_type"] == StatusType.FORWARD_ALIAS_TO_OUTSIDE:
                        logger.info(
                            "Mail should originally be forwarded FROM a local alias TO the "
                            "outside. Informing local user."
                        )

                        local, domain = envelope.rcpt_tos[0].split("@")
                        try:
                            alias = get_alias_by_local_and_domain(db, local=local, domain=domain)
                        except NoResultFound:
                            logger.info("Alias does not exist. We can't inform the user.")
                            return status.E200

                        logger.info("Alias exists. Informing user.")

                        send_mail(
                            message=draft_message(
                                subject="Your mail could not be delivered",
                                template="not-deliverable-to-web",
                                context={
                                    "title": "Your mail could not be delivered",
                                    "preview_text": "Your mail could not be delivered",
                                    "body":
                                        f"We are sorry, but we couldn't deliver your email to "
                                        f"{data['outside_address']}. We tried to send it, "
                                        f"but the user's server couldn't receive it.",
                                    "explanation":
                                        "We recommend you to try it again later. "
                                        "This is probably a temporary issue only.",
                                    "server_url": life_constants.APP_DOMAIN,
                                }
                            ),
                            to_mail=alias.user.email.address,
                            extra_headers={
                                headers.IN_REPLY_TO: extract_in_reply_to_header(report_message),
                            }
                        )

                        return status.E200
                    elif data["status_type"] == StatusType.FORWARD_OUTSIDE_TO_ALIAS:
                        logger.info(
                            "Mail should originally be forwarded FROM the outside TO a local alias. "
                            "Informing outside user."
                        )

                        send_mail(
                            message=draft_message(
                                subject="Your mail could not be delivered",
                                template="not-deliverable-to-web",
                                context={
                                    "title": "Your mail could not be delivered",
                                    "preview_text": "Your mail could not be delivered",
                                    "body":
                                        f"We are sorry, but we couldn't deliver your email to "
                                        f"{data['outside_address']}. We tried to send it, "
                                        f"but the user's server couldn't receive it.",
                                    "explanation":
                                        "We recommend you to try it again later. "
                                        "This is probably a temporary issue only.",
                                    "server_url": life_constants.APP_DOMAIN,
                                }
                            ),
                            to_mail=envelope.rcpt_tos[0],
                            extra_headers={
                                headers.REPLY_TO: extract_in_reply_to_header(report_message),
                            }
                        )

                        return status.E200
                    elif data["status_type"] == StatusType.BOUNCE:
                        logger.info("Mail is a bounce mail from us. Nothing to do.")

                        return status.E200
                    elif data["status_type"] == StatusType.OFFICIAL:
                        # Todo: Inform admins
                        return status.E200

            logger.info("Checking if mail is a normal bounce mail.")
            if is_not_deliverable(envelope, message):
                logger.info("Mail is a bounce mail. No further action required.")
                return status.E200

            logger.info(
                f"Checking if DESTINATION mail {envelope.rcpt_tos[0]} is a relay address."
            )

            if (result := extract_alias_address(envelope.rcpt_tos[0])) is not None:
                # LOCALLY saved user wants to send a mail FROM alias TO the outside.
                alias_address, target = result

                await handle_local_to_outside(
                    db,
                    alias_address=alias_address,
                    target=target,
                    message=message,
                    envelope=envelope,
                    message_id=message_id,
                )

                return status.E200

            logger.info(
                f"Checking if DESTINATION mail {envelope.rcpt_tos[0]} is an alias mail."
            )

            local, domain = envelope.rcpt_tos[0].split("@")
            try:
                alias = get_alias_by_local_and_domain(db, local=local, domain=domain)
            except NoResultFound:
                pass
            else:
                handle_outside_to_local(
                    db,
                    alias=alias,
                    message=message,
                    envelope=envelope,
                    message_id=message_id,
                )

                return status.E200

            logger.info(
                f"Checking if DESTINATION mail {envelope.rcpt_tos[0]} is an reserved alias mail."
            )
            local, domain = envelope.rcpt_tos[0].split("@")
            if reserved_alias := get_reserved_alias_by_address(db, local=local, domain=domain):
                # OUTSIDE user wants to send a mail TO a reserved alias.
                validate_alias(reserved_alias)

                set_header(
                    message,
                    headers.KLECK_FORWARD_STATUS,
                    generate_forward_status(
                        StatusType.OFFICIAL,
                        outside_address=envelope.mail_from,
                        message_id=message_id,
                    )
                )

                for user in reserved_alias.users:
                    send_mail(
                        message,
                        from_mail=reserved_alias.create_outside_email(envelope.mail_from),
                        from_name=envelope.mail_from,
                        to_mail=user.email.address,
                    )
                server_statistics.add_sent_email(db)

                return status.E200

            logger.info(
                f"Mail {envelope.mail_from} is neither a locally saved user nor does it want to "
                f"send to one. Sending error mail back."
            )
            raise AliasNotFoundError(status_code=status.E515)
        except EmailHandlerError as error:
            logger.info(f"Error occurred: {error.reason}")

            send_mail(
                message=draft_message(
                    subject="Your email could not be delivered",
                    template="not-deliverable-to-server",
                    context={
                        "title": "We didn't know what to do with your email",
                        "preview_text": "We could not deliver your email.",
                        "body":
                            f"We are sorry, but we couldn't deliver your email to "
                            f"{envelope.rcpt_tos[0]}. We received it, "
                            f"but we couldn't process it."
                        ,
                        "explanation": error.reason,
                        "server_url": life_constants.APP_DOMAIN,
                    },
                ),
                to_mail=envelope.mail_from,
                extra_headers={
                    headers.IN_REPLY_TO: original_message_id,
                }
            )

            return error.status_code or status.E501
        except Exception as error:
            logging.error(error, exc_info=True)
            logger.info("Exception occurred.")

            return status.E501
