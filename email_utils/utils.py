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
from typing import Optional

import email_normalize
from sqlalchemy.orm import Session

from app import constants, life_constants
from app.models import Email, EmailAlias, LanguageType, User
from email_utils import status
from email_utils.errors import AliasNotFoundError, InvalidEmailError

__all__ = [
    "generate_message_id",
    "message_to_bytes",
    "parse_destination_email",
    "get_local_email",
    "get_alias_by_email",
    "determine_text_language",
    "get_header_unicode",
    "DataclassJSONEncoder"
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
    except:
        pass

    return message_string.encode(errors="replace")


def get_user_aliases(user: User, /) -> set[EmailAlias]:
    return {
        alias
        for alias in user.email_aliases
    }


def find_alias_for_full_address(user: User, /, email: str) -> EmailAlias:
    for alias in get_user_aliases(user):
        if email.endswith(f"_{alias.address}"):
            return alias

    raise AliasNotFoundError(status_code=status.E502)


def parse_destination_email(user: User, email: str) -> tuple[EmailAlias, str]:
    """Parses the `to` email address.

    Returns a tuple containing:
        (local address, targeted address)

    The local address is the locally stored email address to which the email originally was sent to.
    The targeted address is the actual targeted email address to which the email has to be
    relayed to.

    Example:
        email = "test_at_example.com_abcdef@mail.kleckrelay.com"

        Output:
            ("abcdef@mail.kleckrelay.com", "test@example.com")
    """
    local_alias = find_alias_for_full_address(user, email)
    raw_destination = email[:-len(local_alias.address) - 1]

    if raw_destination.count("_at_") != 1:
        raise InvalidEmailError()

    destination_address = raw_destination.replace("_at_", "@")

    if re.match(constants.EMAIL_REGEX, destination_address) is None:
        raise InvalidEmailError()

    return local_alias, destination_address


async def sanitize_email(email: str) -> str:
    normalizer = email_normalize.Normalizer()

    return (await normalizer.normalize(email)).normalized_address


def get_local_email(db: Session, /, email: str) -> Optional[Email]:
    return db.query(Email).filter_by(address=email).first()


def get_alias_by_email(db: Session, /, email: str) -> Optional[EmailAlias]:
    local, domain = email.split("@")

    return db\
        .query(EmailAlias)\
        .filter_by(local=local)\
        .filter_by(domain=domain)\
        .first()


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
