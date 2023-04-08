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
        content_message = MIMEMultipart("mixed")

        content_message.attach(MIMEText(html, "html"))
        content_message.attach(MIMEText(plaintext, "plain"))

        content_message[headers.SUBJECT] = subject
        content_message[headers.DATE] = formatters.format_date()
        content_message[headers.MIME_VERSION] = "1.0"

        public_key_message = MIMENonMultipart(
            "application",
            "pgp-keys",
            name="public_key.asc"
        )
        public_key_message.add_header("Content-Transfer-Encoding", "quoted-printable")
        public_key_message.add_header("Content-Description", "OpenPGP public key")
        public_key_message.set_payload(gpg_handler.SERVER_PUBLIC_KEY)

        content_message.attach(public_key_message)

        signed_content = str(
            gpg_handler.sign_message(
                content_message.as_string(),
                clearsign=False,
            )
        )

        signature_message = MIMENonMultipart(
            "application",
            "pgp-signature",
            name="signature.asc"
        )
        signature_message.add_header("Content-Description", "OpenPGP digital signature")
        signature_message.set_payload(signed_content)

        signed_message = MIMEMultipart("signed", protocol="application/pgp-signature")
        signed_message.attach(content_message)
        signed_message.attach(signature_message)

        encrypted_content = str(
            gpg_handler.encrypt_message(
                signed_message.as_string(),
                gpg_public_key,
            )
        )

        pgp_encrypted_message = MIMENonMultipart(
            "application",
            "octet-stream",
            name="encrypted.asc"
        )
        pgp_encrypted_message.add_header("Content-Description", "OpenPGP encrypted message")
        pgp_encrypted_message.set_payload(encrypted_content)

        message = MIMEMultipart("encrypted", protocol="application/pgp-encrypted")
        message.attach(pgp_encrypted_message)

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

