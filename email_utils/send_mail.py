import smtplib
from email.message import EmailMessage, Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from app import life_constants, logger
from app.models import LanguageType
from . import formatters, headers
from .errors import EmailHandlerError
from .template_renderer import render
from .utils import generate_message_id, message_to_bytes

__all__ = [
    "send_error_mail",
    "send_mail",
    "draft_message",
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

    if life_constants.DEBUG_MAILS:
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


def send_error_mail(
    mail: str,
    targeted_mail: str,
    error: Optional[EmailHandlerError] = None,
    language: LanguageType = LanguageType.EN_US,
) -> None:
    send_mail(
        message=draft_message(
            subject=f"Email could not be delivered to {targeted_mail}.",
            plaintext=render(
                "general_error",
                language,
                error=error,
                targeted_mail=targeted_mail,
            ),
        ),
        from_mail=life_constants.FROM_MAIL,
        to_mail=mail,
    )


def draft_message(
    subject: str,
    plaintext: str,
    html: Optional[str] = None,
) -> Message:
    if html:
        message = MIMEMultipart("alternative")
        message.attach(MIMEText(plaintext))
        message.attach(MIMEText(html, "html"))
    else:
        message = EmailMessage()
        message.set_payload(plaintext)
        message[headers.CONTENT_TYPE] = "text/plain"

    message[headers.SUBJECT] = subject
    message[headers.DATE] = formatters.format_date()
    message[headers.MIME_VERSION] = "1.0"

    return message
