import base64
import enum
import hmac
import re
from datetime import datetime, timedelta
from email.message import Message
from typing import Optional

from aiosmtpd.smtp import Envelope

from app import life_constants, constant_keys, constants
from app.utils.email import is_local_a_bounce_address
from email_utils import headers

__all__ = [
    "StatusType",
    "generate_forward_status",
    "extract_forward_status",
    "is_bounce",
    "is_not_deliverable",
    "get_report_from_message",
]


HEADER_REGEX = re.compile(
    rf"\n{headers.KLECK_FORWARD_STATUS}:\s+([a-z0-9]+\.[a-z0-9]+)\n"
)


class StatusType(enum.Enum):
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


def _create_status_time() -> int:
    diff = datetime.now() - constants.BOUNCE_START_TIME

    return int(diff.total_seconds() / 60)


def _is_status_time_expired(time_in_minutes: int) -> bool:
    diff = timedelta(minutes=time_in_minutes)

    return diff <= constants.BOUNCE_MAX_TIME


# ´message_id` is required to prevent double (handcrafted) bounces
def generate_forward_status(status_type: StatusType, outside_address: str, message_id: str) -> str:
    payload = "=".join([
        status_type.value,
        outside_address,
        message_id[1:-1],
        str(_create_status_time()),
    ]).encode("utf-8")
    signature = _create_signature(payload)

    encoded_payload = base64.b32encode(payload).rstrip(b"=").decode("utf-8").lower()
    encoded_signature = base64.b32encode(signature).rstrip(b"=").decode("utf-8").lower()

    return (
        encoded_payload
        + "."
        + encoded_signature
    )


def extract_forward_status(status: str) -> dict:
    contents = status.split(".")
    if len(contents) != 2:
        raise ValueError("Invalid bounce status payload.")

    payload, signature = contents

    payload_padding = (8 - (len(payload) % 8)) % 8
    payload = base64.b32decode(payload.encode("utf-8").upper() + b"=" * payload_padding)
    signature_padding = (8 - (len(signature) % 8)) % 8
    signature = base64.b32decode(signature.encode("utf-8").upper() + b"=" * signature_padding)

    expected_signature = _create_signature(payload)

    if signature != expected_signature:
        raise ValueError("Invalid bounce status signature.")

    status_type, outside_address, message_id, bounce_time_raw = payload.decode("utf-8").split("=")
    bounce_time = int(bounce_time_raw)

    if _is_status_time_expired(bounce_time):
        raise ValueError("Bounce status payload expired.")

    return {
        "status_type": StatusType(status_type),
        "outside_address": outside_address,
        "message_id": message_id,
        "bounce_time": bounce_time,
    }


def extract_forward_status_header(message: Message) -> Optional[str]:
    if (result := HEADER_REGEX.search(message.as_string())) is not None:
        return result.group(1)


def is_bounce(envelope: Envelope, message: Message) -> bool:
    return envelope.mail_from == "<>" and message.get_content_type().lower() == "multipart/report"


def is_not_deliverable(envelope: Envelope, message: Message) -> bool:
    return \
        envelope.mail_from == "<>" \
        or is_local_a_bounce_address(message.get(headers.FROM).split("@")[0])


def get_report_from_message(message: Message) -> Optional[Message]:
    for part in message.walk():
        if part.get_content_type().lower() == "message/rfc822":
            return part.get_payload()[0]
