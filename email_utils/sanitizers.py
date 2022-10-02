from mailbox import Message

from aiosmtpd.smtp import Envelope

from .validators import validate_envelope

__all__ = [
    "sanitize_envelope",
]


def sanitize_mail(mail: str) -> str:
    return mail.strip().replace(" ", "").replace("\n", " ")


def sanitize_envelope(envelope: Envelope) -> None:
    envelope.mail_from = sanitize_mail(envelope.mail_from)
    envelope.rcpt_tos = [
        sanitize_mail(mail)
        for mail in envelope.rcpt_tos
    ]

    validate_envelope(envelope)


def sanitize_message_header(message: Message, header: str) -> None:
    """remove trailing space and remove linebreak from a header"""
    for i in reversed(range(len(message._headers))):
        header_name = message._headers[i][0].lower()

        if header_name == header.lower():
            # msg._headers[i] is a tuple like ('From', 'hey@google.com')
            if message._headers[i][1]:
                message._headers[i] = (
                    message._headers[i][0],
                    message._headers[i][1].strip().replace("\n", " "),
                )


def sanitize_message(message: Message) -> None:
    sanitize_message_header(message, "from")
    sanitize_message_header(message, "to")
    sanitize_message_header(message, "cc")
    sanitize_message_header(message, "reply-to")
