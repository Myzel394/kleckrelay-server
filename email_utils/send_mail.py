import smtplib
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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
    message: MIMEBase,
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
    message: MIMEBase,
    from_address: str,
    to_address: str,
) -> None:
    logger.info("<===============> SEND email <===============>")
    logger.info(f"FROM {from_address} ----> TO ----> {to_address}")
    logger.info("Content:")
    logger.info(message)
    logger.info("<===============> SEND email --- END --- <===============>")


def send_mail(
    to_mail: str,
    subject: str,
    plaintext: str,
    html: Optional[str] = None,
    from_mail: str = life_constants.FROM_MAIL,
    from_name: str = life_constants.FROM_MAIL,
):
    if html:
        message = MIMEMultipart("alternative")
        message.attach(MIMEText(plaintext))
        message.attach(MIMEText(html, "html"))
    else:
        message = EmailMessage()
        message.set_payload(plaintext)
        message[headers.CONTENT_TYPE] = "text/plain"

    message[headers.SUBJECT] = subject
    message[headers.FROM] = formatters.format_from_mail(
        name=from_name,
        mail=from_mail,
    )
    message[headers.TO] = to_mail
    message[headers.MESSAGE_ID] = generate_message_id()
    message[headers.MIME_VERSION] = "1.0"

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


def send_mail_from_private_mail_to_destination(envelope: Envelope, email: Email) -> None:
    local_alias, forward_address = parse_destination_email(
        user=email.user,
        email=envelope.rcpt_tos[0],
    )
    logger.info(
        f"Email {local_alias} should be relayed to {forward_address}. "
        f"Sending email now..."
    )

    send_mail(
        from_mail=local_alias,
        to_mail=forward_address,
        plaintext=envelope.original_content,
        subject="Test",
    )


def send_mail_from_outside_to_private_mail(envelope: Envelope, alias: EmailAlias) -> None:
    send_mail(
        from_mail=envelope.mail_from,
        to_mail=alias.user.email.address,
        plaintext=envelope.original_content,
        subject="Test",
    )
