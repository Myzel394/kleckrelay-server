import base64
import enum
import hmac
import json
from datetime import datetime
from email.message import Message

from aiosmtpd.smtp import Envelope
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app import life_constants, constant_keys, constants, logger
from app.controllers.mail_bounce_status import create_bounce_status, get_bounce_status_by_id
from app.models import EmailAlias, MailBounceStatus
from app.utils.email import is_local_forbidden
from email_utils import headers

__all__ = [
    "VerpType",
    "generate_verp",
    "extract_verp",
    "is_verp_bounce",
    "has_verp",
    "is_bounce"
]


class VerpType(enum.Enum):
    # Used for official emails sent by the app
    # Example: password reset, email verification etc.
    # They don't need to be tracked
    OFFICIAL = "o"
    # Used for emails sent from or to aliases
    # Example: hezuifh@kleck.app, hello_at_example.com_auivniu@kleck.app etc.
    FORWARD_ALIAS_TO_OUTSIDE = "ao"
    FORWARD_OUTSIDE_TO_ALIAS = "oa"
    # Used for emails that act as bounce messages
    # Example:
    #  - User sends an email to an alias
    #  - The alias forwards the email to the outside
    #  - The email bounces and the bounce message is sent to the alias
    #  - The alias forwards the bounce message to the user
    #  - The bounce message is bounced back to the alias
    # If we would not track this rebounce, there would be an infinite loop
    BOUNCE = "b"


def _create_signature(payload: bytes) -> bytes:
    return hmac.new(
        constant_keys.VERP_SECRET.encode("utf-8"),
        payload,
        life_constants.VERP_HMAC_ALGORITHM
    ).digest()[:8]


def generate_verp(db: Session, /, from_address: str, to_address: str) -> str:
    """
    Variable envelope return path is a technique used to enable automatic detection and removal 
    of undeliverable e-mail addresses (Wikipedia).
    We generate for each mail a unique VERP address to detect when there's a bounce.
    :return: 
    """
    logger.info("Generating VERP address...")
    bounce_status = create_bounce_status(
        db,
        from_address=from_address,
        to_address=to_address,
    )
    logger.info(f"Created bounce status with id {bounce_status.id}")
    payload = json.dumps([
        str(bounce_status.id),
    ]).encode("utf-8")
    signature = _create_signature(payload)
    # We only have a very limited number of characters available for the VERP address
    # We strip the padding and add it in the extraction process again
    encoded_payload = base64.b32encode(payload).rstrip(b"=").decode("utf-8")
    encoded_signature = base64.b32encode(signature).rstrip(b"=").decode("utf-8")

    address = (".".join([
        constants.VERP_PREFIX,
        encoded_payload,
        encoded_signature,
    ]) + "@" + life_constants.MAIL_DOMAIN).lower()

    logger.info(f"Generated VERP address {address}.")

    return address


def extract_verp(db: Session, /, local: str) -> MailBounceStatus:
    fields = local.split(".")

    if len(fields) != 3:
        raise ValueError("Invalid VERP address.")

    if fields[0] != constants.VERP_PREFIX:
        raise ValueError("No VERP prefix.")

    payload_padding = (8 - (len(fields[1]) % 8)) % 8
    payload = base64.b32decode(fields[1].encode("utf-8").upper() + b"=" * payload_padding)
    signature_padding = (8 - (len(fields[2]) % 8)) % 8
    signature = base64.b32decode(fields[2].encode("utf-8").upper() + b"=" * signature_padding)

    expected_signature = _create_signature(payload)

    if signature != expected_signature:
        raise ValueError("Invalid VERP signature.")

    bounce_status_id = json.loads(payload)[0]

    try:
        bounce_status = get_bounce_status_by_id(db, bounce_status_id)
    except NoResultFound:
        raise ValueError("Invalid VERP payload.")

    if bounce_status.is_expired:
        raise ValueError("VERP payload expired.")

    return bounce_status


def is_verp_bounce(envelope: Envelope) -> bool:
    """Detect whether an email is a Delivery Status Notification"""
    return envelope.rcpt_tos[0].startswith(constants.VERP_PREFIX)


def has_verp(message: Message) -> bool:
    return message.get(headers.RETURN_PATH, "").startswith(constants.VERP_PREFIX)


def is_bounce(envelope: Envelope) -> bool:
    return\
        not envelope.mail_from\
        or envelope.mail_from == "<>"\
        or is_local_forbidden(envelope.rcpt_tos[0].split("@")[0])
