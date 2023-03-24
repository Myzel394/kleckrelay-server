import dataclasses
import json
import os
import random
import re
import socket
import time
from email import policy
from email.header import decode_header
from email.message import Message
from typing import Generator, Optional

import email_normalize
from sqlalchemy.orm import Session

from app import constants, life_constants, logger
from app.models import Email, EmailAlias, LanguageType, User
from email_utils import status
from email_utils.errors import AliasNotFoundError

__all__ = [
    "generate_message_id",
    "message_to_bytes",
    "get_alias_by_email",
    "determine_text_language",
    "get_header_unicode",
    "DataclassJSONEncoder",
    "extract_alias_address",
    "get_alias_from_user",
]

USER_EMAIL_CONTENT_TYPES = [
    "text/html",
    "text/plain",
]


def generate_message_id(
    message_id: str = None,
    domain: str = life_constants.MAIL_DOMAIN,
) -> str:
    timeval = int(time.time()*100)
    pid = os.getpid()
    randint = random.getrandbits(64)
    idstring = "" if message_id is None else f".{message_id}"
    message_domain = domain or socket.getfqdn()

    return "<%d.%d.%d%s@%s>" % (timeval, pid, randint, idstring, message_domain)


def message_to_bytes(message: Message) -> bytes:
    for generator_policy in [None, policy.SMTP, policy.SMTPUTF8]:
        try:
            return message.as_bytes(policy=generator_policy)
        except:
            pass

    message_string = message.as_string()

    try:
        return message_string.encode()
    except UnicodeEncodeError:
        pass

    return message_string.encode(errors="replace")


def find_alias_for_full_address(user: User, /, email: str) -> EmailAlias:
    for alias in user.email_aliases:
        if email.endswith(f"_{alias.address}"):
            return alias

    raise AliasNotFoundError(status_code=status.E502)


def extract_alias_address(address: str) -> Optional[tuple[str, str]]:
    """Extracts an alias address.
    This only extracts the address, it does not validate it.

    Returns a tuple containing:
        (local address, targeted address)
    Returns `None` if the address is not of valid format.

    The local address is the locally stored email address to which the email originally was sent to.
    The targeted address is the actual targeted email address to which the email has to be
    relayed to.

    Example:
        email = "test_at_example.com_abcdef@mail.kleckrelay.com"

        Output:
            ("abcdef@mail.kleckrelay.com", "test.yaml@example.com")
    """
    groups = re.match(constants.ALIAS_OUTSIDE_REGEX, address)

    if groups is None:
        return None

    target_local = groups.group(1)
    target_domain = groups.group(2)
    alias = groups.group(3)

    target = f"{target_local}@{target_domain}"

    return alias, target


async def sanitize_email(email: str) -> str:
    normalizer = email_normalize.Normalizer()

    return (await normalizer.normalize(email)).normalized_address


def get_email_by_from(db: Session, /, email: str) -> Optional[Email]:
    return db.query(Email).filter_by(address=email).one()


def get_alias_by_email(db: Session, /, email: str) -> Optional[EmailAlias]:
    local, domain = email.split("@")

    return db\
        .query(EmailAlias)\
        .filter_by(local=local)\
        .filter_by(domain=domain)\
        .first()


def get_alias_from_user(db: Session, /, user: User, local: str, domain: str) -> EmailAlias:
    return db\
        .query(EmailAlias)\
        .filter_by(local=local)\
        .filter_by(domain=domain)\
        .filter_by(user_id=user.id)\
        .one()


def determine_text_language(text: str) -> LanguageType:
    return LanguageType.EN_US


def get_header_unicode(header: str) -> str:
    if header is None:
        return ""

    value = ""
    for to_decoded_str, charset in decode_header(header):
        if charset is None:
            if type(to_decoded_str) is bytes:
                decoded_str = to_decoded_str.decode()
            else:
                decoded_str = to_decoded_str
        else:
            try:
                decoded_str = to_decoded_str.decode(charset)
            except (LookupError, UnicodeDecodeError):  # charset is unknown
                try:
                    decoded_str = to_decoded_str.decode("utf-8")
                except UnicodeDecodeError:
                    decoded_str = to_decoded_str.decode("utf-8", errors="replace")
        value += decoded_str

    return value


# https://stackoverflow.com/a/51286749/9878135
class DataclassJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return o.as_dict()
        return super().default(o)


def find_email_content(message: Message) -> Generator[tuple[Message, str], None, None]:
    """Return the content(s) of the message.

    Only returns the content that will be visible to the user (encrypted content, attachments,
    etc. are ignored).
    """
    content = message.get_payload(decode=True) or message.get_payload()
    logger.info("Parsing content.")
    if type(content) is bytes:
        # Try to get the payload firstly and fallback then
        content = message.get_payload() or message.get_payload(decode=True)

    if type(content) is str:
        logger.info("Found 1 content.")

        if message.get_content_type() in USER_EMAIL_CONTENT_TYPES:
            yield message, content

    elif type(content) is list:
        logger.info(f"Found {len(content)} contents.")

        for part in message.walk():
            if part.get_content_type() in USER_EMAIL_CONTENT_TYPES:
                yield part, part.get_payload() or part.get_payload(decode=True)
