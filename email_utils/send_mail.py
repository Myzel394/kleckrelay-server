import smtplib
import time
from email.message import EmailMessage, Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Optional

from app import life_constants, logger
from app.models import LanguageType
from . import formatters, headers
from .dkim_signature import add_dkim_signature
from .errors import EmailHandlerError
from .headers import delete_header, set_header
from .template_renderer import render
from .utils import message_to_bytes

__all__ = [
    "send_error_mail",
    "send_mail",
    "draft_message",
    "send_template_mail",
]


def _send_mail_to_smtp_server(
    message: Message,
    from_address: str,
    to_address: str,
) -> None:
    logger.info(
        f"Send mail -> Sending mail {from_address=} {to_address=}; "
        f"Postfix Host={life_constants.POSTFIX_HOST}, Postfix Port={life_constants.POSTFIX_PORT}.")
    with smtplib.SMTP(host=life_constants.POSTFIX_HOST, port=life_constants.POSTFIX_PORT) as smtp:
        logger.info("Send mail -> Activating TLS.")
        time.sleep(1)
        smtp.starttls()

        logger.info("Send mail -> Sending mail now.")
        smtp.sendmail(
            from_addr=from_address,
            to_addrs=to_address,
            msg=message_to_bytes(message),
        )
        logger.info("Send mail -> Mail sent successfully.")


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
    logger.info(f"Send Mail -> Send new mail {from_mail=} {to_mail=}.")
    from_name = from_name or from_mail

    set_header(
        message,
        headers.FROM,
        formatters.format_from_mail(name=from_name, mail=from_mail)
    )
    set_header(
        message,
        headers.TO, to_mail
    )

    #add_dkim_signature(message)

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
    from_mail: str,
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
        to_mail=from_mail,
    )


def send_template_mail(
    template: str,
    subject: str,
    to: str,
    language: LanguageType = LanguageType.EN_US,
    from_address: str = life_constants.FROM_MAIL,
    from_name: str = life_constants.SUPPORT_MAIL_FROM_NAME,
    context: dict[str, Any] = None,
) -> None:
    send_mail(
        message=draft_message(
            subject=subject,
            plaintext=render(
                template,
                language,
                **(context or {})
            ),
        ),
        from_name=from_name,
        from_mail=from_address,
        to_mail=to,
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

    # Those headers will be replaced by `send_mail`
    message[headers.FROM] = "ReplaceMe"
    message[headers.TO] = "ReplaceMe"

    message[headers.SUBJECT] = subject
    message[headers.DATE] = formatters.format_date()
    message[headers.MIME_VERSION] = "1.0"

    return message

