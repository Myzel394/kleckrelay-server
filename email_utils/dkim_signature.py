import base64

import dkim

from email.message import Message

from app import life_constants, logger
from . import headers
from .headers import delete_header, set_header
from .utils import message_to_bytes


__all__ = [
    "add_dkim_signature"
]

DKIM_PRIVATE_KEY = base64.b64decode(life_constants.DKIM_PRIVATE_KEY).decode()


def add_dkim_signature(
    message: Message,
) -> None:
    if not DKIM_PRIVATE_KEY:
        logger.info("Add DKIM signature: No private key specified.")
        return

    logger.info("Add DKIM signature -> Creating new DKIM signature.")

    for dkim_headers in headers.DKIM_HEADERS:
        logger.info(f"Add DKIM signature -> Trying with headers {dkim_headers}.")
        try:
            _create_dkim_signature(message, dkim_headers)
            return
        except dkim.DKIMException:
            logger.info(f"Add DKIM signature -> Trying with headers {dkim_headers} - FAILED!")
            # Try with different headers
            continue


def _create_dkim_signature(
    message: Message, dkim_headers: [bytes]
) -> None:
    # Reset header
    delete_header(message, headers.DKIM_SIGNATURE)

    email_domain = message[headers.FROM].split("@")[1]

    logger.info(f"Create DKIM signature -> Creating signature with {dkim_headers=}.")
    signature = dkim.sign(
        message=message_to_bytes(message),
        selector=b"dkim",
        domain=email_domain.encode(),
        privkey=DKIM_PRIVATE_KEY.encode(),
        include_headers=dkim_headers,
    ).decode()

    # Remove linebreaks from signature
    signature = signature.replace("\n", " ").replace("\r", "")

    # Add signature
    message[headers.DKIM_SIGNATURE] = signature[len(f"{headers.DKIM_SIGNATURE}: "):]
    logger.info(f"Create DKIM signature -> Signature created successfully.")
