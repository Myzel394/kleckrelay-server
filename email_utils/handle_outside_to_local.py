from email.message import Message

from aiosmtpd.smtp import Envelope
from sqlalchemy.orm import Session

from app.controllers import server_statistics
from app.controllers import global_settings as settings
from app import logger
from app.controllers.email_report import create_email_report
from app.email_report_data import EmailReportData
from app.models import EmailAlias
from email_utils import headers
from email_utils.bounce_messages import generate_forward_status, StatusType
from email_utils.content_handler import (
    convert_images, expand_shortened_urls,
    remove_image_trackers,
)
from email_utils.headers import set_header
from email_utils.send_mail import send_mail
from email_utils.utils import get_header_unicode
from email_utils.validators import validate_alias


__all__ = [
    "handle_outside_to_local"
]


def handle_outside_to_local(
    db: Session,
    /,
    envelope: Envelope,
    message: Message,
    alias: EmailAlias,
    message_id: str,
) -> None:
    logger.info("Mail is an alias mail (OUTSIDE wants to send to LOCAL).")

    logger.info("Checking if alias is valid.")

    # OUTSIDE user wants to send a mail TO a locally saved user's private mail.
    validate_alias(alias)

    logger.info("Alias is valid.")

    report = EmailReportData(
        mail_from=envelope.mail_from,
        mail_to=alias.address,
        subject=get_header_unicode(message[headers.SUBJECT]),
        message_id=message[headers.MESSAGE_ID],
    )

    content = message.get_payload()

    if type(content) is str:
        content_type = message.get_content_type()

        if content_type == "text/html":
            content = parse_html(
                db,
                alias=alias,
                report=report,
                content=content,
            )

            message.set_payload(content, "utf-8")
        elif content_type == "text/plain":
            content = parse_text(
                alias=alias,
                content=content,
            )

            message.set_payload(content, "utf-8")
    elif type(content) is list:
        content_maps = {
            part.get_content_type(): part.get_payload()
            for part in message.walk()
        }

        if "text/html" in content_maps:
            content_maps["text/html"] = parse_html(
                db,
                alias=alias,
                report=report,
                content=content_maps["text/html"],
            )

        if "text/plain" in content_maps:
            content_maps["text/plain"] = parse_text(
                alias=alias,
                content=content_maps["text/plain"],
            )

    if alias.create_mail_report and alias.user.public_key is not None:
        create_email_report(
            db,
            report_data=report,
            user=alias.user,
        )

    logger.info(
        f"Email {envelope.mail_from} is from outside and wants to send to alias "
        f"{alias.address}. "
        f"Relaying email to locally saved user {alias.user.email.address}."
    )

    set_header(
        message,
        headers.KLECK_FORWARD_STATUS,
        generate_forward_status(
            StatusType.FORWARD_OUTSIDE_TO_ALIAS,
            outside_address=envelope.mail_from,
            message_id=message_id,
        )
    )

    send_mail(
        message,
        from_mail=alias.create_outside_email(envelope.mail_from),
        from_name=envelope.mail_from,
        to_mail=alias.user.email.address,
    )
    server_statistics.add_sent_email(db)


def parse_text(
    alias: EmailAlias,
    content: str,
) -> str:
    return content


def parse_html(
    db: Session,
    /,
    alias: EmailAlias,
    report: EmailReportData,
    content: str,
) -> str:
    enable_image_proxy = settings.get(db, "ENABLE_IMAGE_PROXY")

    if alias.remove_trackers:
        logger.info("Removing single pixel image trackers.")
        content = remove_image_trackers(report, html=content)

    if enable_image_proxy and alias.proxy_images:
        logger.info("Converting images to proxy links.")
        content = convert_images(report, alias=alias, html=content)

    if alias.expand_url_shorteners:
        logger.info("Expanding shortened URLs.")
        content = expand_shortened_urls(report, alias=alias, html=content)

    server_statistics.add_removed_trackers(db, len(report.single_pixel_images))
    server_statistics.add_proxied_images(db, len(report.proxied_images))
    server_statistics.add_expanded_urls(db, len(report.expanded_urls))

    return content
