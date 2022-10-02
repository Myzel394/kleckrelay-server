from mailbox import Message

from aiosmtpd.smtp import Envelope
from sqlalchemy.orm import Session

from app.models import EmailReport

__all__ = [
    "creat_email_report",
]


def _generate_data(
    message: Message,
    envelope: Envelope,
) -> dict:
    return {
        "version": 1.0,
        "mail_details": {
            "from": envelope.mail_from,
            "to": envelope.rcpt_tos[0],
        }
    }


def creat_email_report(
    db: Session,
    /,
    message: Message,
    envelope: Envelope,
) -> EmailReport:
    pass
