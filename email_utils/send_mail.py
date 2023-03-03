import smtplib
import time
from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Optional
import lxml.html
from pyquery import PyQuery as pq

from app import life_constants, logger
from app.models import LanguageType
from . import formatters, headers
from .bounce_messages import generate_forward_status, StatusType
from .errors import EmailHandlerError
from .headers import set_header
from .template_renderer import render
from .utils import message_to_bytes

__all__ = [
    "send_mail",
    "draft_message",
]


def _send_mail_to_smtp_server(
    message: Message,
    from_address: str,
    to_address: str,
) -> None:
    logger.info(
        f"Send mail -> Sending mail {from_address=} {to_address=}; "
        f"Postfix Host={life_constants.POSTFIX_HOST}, Postfix Port={life_constants.POSTFIX_PORT}."
    )
    with smtplib.SMTP(host=life_constants.POSTFIX_HOST, port=life_constants.POSTFIX_PORT) as smtp:
        logger.info("Send mail -> Activating TLS.")
        if life_constants.IS_DEBUG:
            time.sleep(1)

        if not life_constants.IS_DEBUG:
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
    logger.info(message.as_string())
    logger.info("<===============> SEND email --- END --- <===============>")


def send_mail(
    message: Message,
    to_mail: str,
    from_mail: str = life_constants.FROM_MAIL,
    from_name: Optional[str] = None,
    extra_headers: dict[str, str] = None,
):
    logger.info(f"Send Mail -> Send new mail {from_mail=} {to_mail=}.")
    from_name = from_name or from_mail

    if extra_headers:
        for header, value in extra_headers.items():
            set_header(message, header, value)

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


def draft_message(
    subject: str,
    template: str,
    bounce_status: StatusType = StatusType.OFFICIAL,
    context: dict[str, Any] = None,
) -> Message:
    html = render(
        f"{template}.html",
        **context,
    )
    plaintext = render(
        f"{template}.jinja2",
        **context,
    )

    message = MIMEMultipart("alternative")
    message.attach(MIMEText(html, "html"))
    message.attach(MIMEText(plaintext, "plain"))

    # Those headers will be replaced by `send_mail`
    message[headers.FROM] = "ReplaceMe"
    message[headers.TO] = "ReplaceMe"

    message[headers.SUBJECT] = subject
    message[headers.DATE] = formatters.format_date()
    message[headers.MIME_VERSION] = "1.0"

    message[headers.KLECK_FORWARD_STATUS] = generate_forward_status(bounce_status)

    return message

