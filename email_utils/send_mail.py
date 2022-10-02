import smtplib
from email.message import Message
from typing import Optional

from aiosmtpd.smtp import Envelope

from app import life_constants, logger
from app.models import Email, EmailAlias
from . import formatters, headers
from .utils import generate_message_id, message_to_bytes, parse_destination_email

__all__ = [
    "send_mail_from_private_mail_to_destination",
    "send_mail_from_outside_to_private_mail",
]


def _send_mail_to_smtp_server(
    message: Message,
    from_address: str,
    to_address: str,
) -> None:
    with smtplib.SMTP(host=life_constants.POSTFIX_HOST, port=life_constants.POSTFIX_PORT) as smtp:
        if life_constants.POSTFIX_USE_TLS:
            smtp.starttls()

        smtp.sendmail(
            from_addr=from_address,
            to_addrs=to_address,
            msg=message_to_bytes(message),
        )


def _debug_email(
    message: Message,
    from_address: str,
    to_address: str,
) -> None:
    logger.info("<===============> SEND email <===============>")
    logger.info(f"FROM {from_address} ----> TO ----> {to_address}")
    logger.info("Content:")
    logger.info(message)
    logger.info("<===============> SEND email --- END --- <===============>")


def send_mail(
    message: Message,
    to_mail: str,
    from_mail: str = life_constants.FROM_MAIL,
    from_name: Optional[str] = None,
):
    from_name = from_name or from_mail

    message[headers.FROM] = formatters.format_from_mail(
        name=from_name,
        mail=from_mail,
    )
    message[headers.TO] = to_mail
    message[headers.MESSAGE_ID] = generate_message_id()

    if life_constants.DEBUG_EMAILS:
        _debug_email(
            message=message, 
            to_address=to_mail, 
            from_address=from_mail
        )
    else:
        _send_mail_to_smtp_server(
            message=message,
            to_address=to_mail,
            from_address=from_mail,
        )


def send_mail_from_private_mail_to_destination(
    envelope: Envelope,
    message: Message,
    email: Email,
) -> None:
    local_alias, forward_address = parse_destination_email(
        user=email.user,
        email=envelope.rcpt_tos[0],
    )
    logger.info(
        f"Local mail {local_alias} should be relayed to outside mail {forward_address}. "
        f"Sending email now..."
    )

    send_mail(
        from_mail=local_alias,
        to_mail=forward_address,
        message=message,
    )


def send_mail_from_outside_to_private_mail(
    envelope: Envelope,
    message: Message,
    alias: EmailAlias,
) -> None:
    logger.info(
        f"Outside mail {envelope.mail_from} should be relayed to private mail "
        f"{alias.user.email.address} (from alias {alias.address})."
    )

    send_mail(
        from_mail=envelope.mail_from,
        to_mail=alias.user.email.address,
        message=message,
    )
