import base64
import enum
import hmac
import json
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
    "extract_forward_status_header",
    "extract_in_reply_to_header",
]


FORWARD_STATUS_HEADER_REGEX = re.compile(
    rf"\n{headers.KLECK_FORWARD_STATUS}:\s+([a-z0-9]+\.[a-z0-9]+)\n"
)
IN_REPLY_TO_HEADER_REGEX = re.compile(
    rf"\n{headers.IN_REPLY_TO}:\s+( -~)\n"
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
    ).digest()


def _create_status_time() -> int:
    diff = datetime.utcnow() - constants.BOUNCE_START_TIME

    return int(diff.total_seconds() / 60)


def _is_status_time_expired(time_in_minutes: int) -> bool:
    diff = timedelta(minutes=time_in_minutes)

    return diff <= constants.BOUNCE_MAX_TIME


# ´message_id` is required to prevent double (handcrafted) bounces
def generate_forward_status(
    status_type: StatusType,
    outside_address: Optional[str] = None,
    message_id: Optional[str] = None,
) -> str:
    payload = base64.b64encode(
        json.dumps({
            "type": status_type.value,
            "outside_address": outside_address,
            "message_id": message_id,
            "time": _create_status_time(),
        }).encode("utf-8")
    )
    signature = _create_signature(payload)

    return (
        payload.decode("utf-8")
        + "."
        + signature.hex()
    )


def extract_forward_status(status: str) -> dict:
    contents = status.split(".")
    if len(contents) != 2:
        raise ValueError("Invalid bounce status payload.")

    raw_payload, signature = contents

    encoded_payload = raw_payload.encode("utf-8")

    expected_signature = _create_signature(encoded_payload)

    if signature != expected_signature.hex():
        raise ValueError("Invalid bounce status signature.")

    payload = json.loads(base64.b64decode(encoded_payload.decode("utf-8")))

    if _is_status_time_expired(payload["time"]):
        raise ValueError("Bounce status payload expired.")

    return payload


def extract_forward_status_header(message: Message) -> Optional[str]:
    if (result := FORWARD_STATUS_HEADER_REGEX.search(message.as_string())) is not None:
        return result.group(1)


def extract_in_reply_to_header(message: Message) -> Optional[str]:
    if (result := IN_REPLY_TO_HEADER_REGEX.search(message.as_string())) is not None:
        return result.group(1)


def is_bounce(envelope: Envelope, message: Message) -> bool:
    return envelope.mail_from == "<>" and message.get_content_type().lower() == "multipart/report"


def is_not_deliverable(envelope: Envelope, message: Optional[Message] = None) -> bool:
    if envelope.mail_from == "<>":
        return True

    if message is None:
        if (from_header := message.get(headers.FROM)) is not None:
            return is_local_a_bounce_address(from_header.split("@")[0])

    return False


def get_report_from_message(message: Message) -> Optional[Message]:
    for part in message.walk():
        if part.get_content_type().lower() == "message/rfc822":
            return part.get_payload()[0]
