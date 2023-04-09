import re
import subprocess
from dataclasses import dataclass
from datetime import date
from typing import Optional
from app import life_constants, constants


@dataclass
class PublicKeyResult:
    fingerprint: str
    type: str
    created_at: date
    # The raw email imported. This is not normalized
    raw_email: str


def find_public_key(email: str) -> Optional[PublicKeyResult]:
    """Try to find the public key for the given `email`.
    Uses web key discovery to find the key.
    If a key is found, it's fingerprint is returned.

    :raises ValueError: If the email is invalid.
    """

    if not life_constants.ENABLE_PGP_KEY_DISCOVERY:
        return None

    # We validate the email again to avoid any possible injection
    email = email.strip()
    if not re.match(constants.EMAIL_REGEX, email):
        raise ValueError("Invalid email address.")

    # We don't want to locate keys locally, as the user can't access the server internally.
    # If there was a key locally, it is most likely fake.
    process = subprocess.Popen(
        ["gpg", "--auto-key-locate", "wkd,ntds,ldap,cert,dane,nodefault", "--locate-key", email],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        raise ValueError(stderr.decode("utf-8"))

    value = stdout.decode("utf-8")
    type_line, fingerprint_line, email_line, _, _ = value.splitlines()

    type_regex_result = re.match(
        constants.GPG_AUTO_LOCATE_KEY_TYPE_REGEX,
        type_line,
    )
    fingerprint_regex_result = re.match(
        constants.GPG_AUTO_LOCATE_KEY_FINGERPRINT_REGEX,
        fingerprint_line,
    )
    email_regex_result = re.match(
        constants.GPG_AUTO_LOCATE_KEY_EMAIL_REGEX,
        email_line,
    )

    if not all((type_regex_result, fingerprint_regex_result, email_regex_result)):
        return None

    return PublicKeyResult(
        fingerprint=fingerprint_regex_result.group(1),
        type=type_regex_result.group(1),
        created_at=date.fromisoformat(type_regex_result.group(2)),
        raw_email=email_regex_result.group(1),
    )

