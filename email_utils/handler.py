import binascii
from mailbox import Message
from typing import Union

from aiosmtpd.smtp import Envelope
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from sqlalchemy.sql import Alias

from app import logger
from app.controllers import global_settings as settings
from app.controllers import server_statistics
from app.controllers.alias import get_alias_by_local_and_domain
from app.controllers.reserved_alias import get_reserved_alias_by_address
from app.database.dependencies import with_db
from app.models import LanguageType, ReservedAlias
from email_utils import status
from email_utils.errors import AliasNotFoundError, EmailHandlerError
from email_utils.send_mail import (
    send_bounce_mail, send_error_mail, send_mail,
)
from email_utils.utils import (
    extract_alias_address, generate_message_id,
)
from email_utils.validators import validate_alias
from . import headers
from .bounce_messages import (
    extract_forward_status, extract_forward_status_header, generate_forward_status,
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
        user = None

        try:
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
                        send_bounce_mail(
                            data["outside_address"],
                            alias.user.email.address,
                            language=alias.user.language,
                        )

                        return status.E200
                    elif data["status_type"] == StatusType.FORWARD_OUTSIDE_TO_ALIAS:
                        logger.info(
                            "Mail should originally be forwarded FROM the outside TO a local alias. "
                            "Informing outside user."
                        )

                        send_bounce_mail(
                            envelope.rcpt_tos[0],
                            data["outside_address"],
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
            if alias := get_alias_by_local_and_domain(db, local=local, domain=domain):
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
            send_error_mail(
                from_mail=envelope.mail_from,
                targeted_mail=envelope.rcpt_tos[0],
                error=error,
                language=user.language if user is not None else LanguageType.EN_US,
            )

            return error.status_code
