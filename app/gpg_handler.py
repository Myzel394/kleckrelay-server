import base64
import sys

import gnupg

from app import life_constants

__all__ = [
    "gpg",
    "encrypt_message",
    "SERVER_PUBLIC_KEY",
    "sign_message",
    "get_public_key_from_fingerprint",
]


PATHS = {
    "darwin": "/opt/homebrew/bin/gpg"
}

gpg = gnupg.GPG(PATHS[sys.platform] if sys.platform in PATHS else None)
gpg.encoding = "utf-8"

__private_key: gnupg.ImportResult = gpg.import_keys(
    base64.b64decode(life_constants.SERVER_PRIVATE_KEY).decode("utf-8")
)
SERVER_PUBLIC_KEY = gpg.export_keys(__private_key.fingerprints[0])


def sign_message(message: str, clearsign: bool = True, detach: bool = True) -> str:
    return gpg.sign(
        message,
        default_key=__private_key.fingerprints[0],
        clearsign=clearsign,
        detach=detach,
    )


def encrypt_message(message: str, public_key_in_str: str) -> gnupg.Crypt:
    public_key: gnupg.ImportResult = gpg.import_keys(public_key_in_str)

    if not public_key.fingerprints:
        raise ValueError("This is not a valid PGP public key.")

    return gpg.encrypt(message, public_key.fingerprints[0])


def get_public_key_from_fingerprint(fingerprint: str) -> gnupg.GPG:
    return gpg.export_keys(fingerprint, minimal=True)

gpg.
