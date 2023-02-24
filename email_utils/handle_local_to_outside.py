from email.message import Message

from aiosmtpd.smtp import Envelope
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app import logger
from app.controllers import server_statistics
from app.controllers.alias import get_alias_by_local_and_domain
from app.controllers.email import get_email_by_address
from app.controllers.reserved_alias import get_reserved_alias_by_address
from app.utils.email import normalize_email
from email_utils import headers
from email_utils.bounce_messages import generate_forward_status, StatusType
from email_utils.errors import AliasNotYoursError
from email_utils.headers import set_header
from email_utils.send_mail import send_mail
from email_utils.validators import validate_alias


__all__ = [
    "handle_local_to_outside"
]


async def handle_local_to_outside(
    db: Session,
    /,
    alias_address: str,
    target: str,
    envelope: Envelope,
    message: Message,
    message_id: str
) -> None:
    # LOCALLY saved user wants to send a mail FROM alias TO the outside.
    from_mail = await normalize_email(envelope.mail_from)
    logger.info(
        f"{envelope.rcpt_tos[0]} is an forward alias address (LOCAL wants to send to "
        f"OUTSIDE). It should be sent to {target} via alias {alias_address} "
        f"Checking if FROM {from_mail} user owns it."
    )

    try:
        email = get_email_by_address(db, from_mail)
    except NoResultFound:
        logger.info(f"User does not exist. Raising error.")
        # Return "AliasNotYoursError" to avoid an alias being leaked
        raise AliasNotYoursError()

    logger.info(f"Checking if user owns the given alias.")
    user = email.user

    local, domain = alias_address.split("@")

    if (alias := get_reserved_alias_by_address(db, local, domain)) is not None:
        logger.info("Alias is a reserved alias.")

        # Reserved alias
        if user not in alias.users:
            logger.info("User is not in reserved alias users. Raising error.")
            raise AliasNotYoursError()
    else:
        # Local alias
        try:
            alias = get_alias_by_local_and_domain(db, local=local, domain=domain)
        except NoResultFound:
            logger.info("Alias does not exist. Raising error.")
            raise AliasNotYoursError()

        if user != alias.user:
            logger.info("User does not own the alias. Raising error.")
            raise AliasNotYoursError()

    logger.info("Checking if alias is valid.")
    validate_alias(alias)
    logger.info("Alias is valid.")

    logger.info(
        f"Local mail {alias.address} should be relayed to outside mail {target}. "
        f"Sending email now..."
    )

    set_header(
        message,
        headers.KLECK_FORWARD_STATUS,
        generate_forward_status(
            StatusType.FORWARD_ALIAS_TO_OUTSIDE,
            outside_address=target,
            message_id=message_id,
        )
    )

    send_mail(
        message,
        from_mail=alias.address,
        to_mail=target,
    )
    server_statistics.add_sent_email(db)
