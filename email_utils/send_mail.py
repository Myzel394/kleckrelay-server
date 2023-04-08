import smtplib
import time
from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.nonmultipart import MIMENonMultipart
from email.mime.text import MIMEText
from typing import Any, Optional

from app import life_constants, logger, gpg_handler
from . import formatters, headers
from .bounce_messages import generate_forward_status, StatusType
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


# Create a email message
def _m(
    klaas: Any,
    *args,
    headers: dict[str, str] = None,
    attachments: list[Message] = None,
    payload: Optional[str] = None,
    name: Optional[str] = None,
    protocol: Optional[str] = None,
) -> Message:
    attachments = attachments or []
    headers = headers or {}
    message = klaas(*args, name=name, protocol=protocol)

    for header, value in headers.items():
        set_header(message, header, value)

    if payload:
        message.set_payload(payload)

    for attachment in attachments:
        message.attach(attachment)

    return message


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
    gpg_public_key: str = None,
) -> Message:
    html = render(
        f"{template}.html",
        **context,
    )
    plaintext = render(
        f"{template}.jinja2",
        **context,
    )

    if gpg_public_key:
        # Thanks to https://datawookie.dev/blog/2021/11/understanding-encrypted-email/
        content_message = _m(
            MIMEMultipart,
            "mixed",
            headers={
                headers.SUBJECT: subject,
                headers.DATE: formatters.format_date(),
                headers.MIME_VERSION: "1.0",
            },
            attachments=[
                MIMEText(html, "html"),
                MIMEText(plaintext, "plain"),
                _m(
                    MIMENonMultipart,
                    "application",
                    "pgp-keys",
                    name="public_key.asc",
                    headers={
                        headers.CONTENT_DESCRIPTION: "OpenPGP public key",
                        headers.CONTENT_TRANSFER_ENCODING: "quoted-printable",
                    },
                    payload=gpg_handler.SERVER_PUBLIC_KEY,
                ),
            ]
        )
        decrypted_message = _m(
            MIMEMultipart,
            "application",
            "signed",
            protocol="application/pgp-signature",
            attachments=[
                content_message,
                _m(
                    MIMENonMultipart,
                    "application",
                    "pgp-signature",
                    name="signature.asc",
                    headers={
                        headers.CONTENT_DESCRIPTION: "OpenPGP digital signature",
                    },
                    payload=str(
                        gpg_handler.sign_message(
                            content_message.as_string(),
                            clearsign=False,
                        )
                    ),
                ),
            ],
        )

        message = _m(
            MIMEMultipart,
            "encrypted",
            protocol="application/pgp-encrypted",
            attachments=[
                MIMEText("Version: 1", "pgp-encrypted"),
                _m(
                    MIMENonMultipart,
                    "application",
                    "octet-stream",
                    name="encrypted.asc",
                    headers={
                        headers.CONTENT_DESCRIPTION: "OpenPGP encrypted message",
                    },
                    payload=str(
                        gpg_handler.encrypt_message(
                            decrypted_message.as_string(),
                            gpg_public_key,
                        )
                    ),
                ),
            ]
        )

    else:
        message = MIMEMultipart("alternative")

        message.attach(MIMEText(html, "html"))
        message.attach(MIMEText(plaintext, "plain"))

        message[headers.SUBJECT] = subject
        message[headers.DATE] = formatters.format_date()
        message[headers.MIME_VERSION] = "1.0"

    # Those headers will be replaced by `send_mail`
    message[headers.FROM] = "ReplaceMe"
    message[headers.TO] = "ReplaceMe"

    message[headers.KLECK_FORWARD_STATUS] = generate_forward_status(bounce_status)

    return message

