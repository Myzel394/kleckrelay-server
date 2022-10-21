import base64

from pretty_bad_protocol import gnupg

from app import life_constants

__all__ = [
    "gpg",
    "sign_and_encrypt_message",
    "encrypt_message",
]

gpg = gnupg.GPG()
gpg.encoding = "utf-8"

SERVER_PRIVATE_KEY = gpg.import_keys(base64.b64decode(life_constants.SERVER_PRIVATE_KEY))
IS_SERVER_KEY_VALID = len(SERVER_PRIVATE_KEY.fingerprints) > 0


def sign_and_encrypt_message(message: str, public_key_in_str: str) -> str:
    if IS_SERVER_KEY_VALID:
        message = gpg.sign(
            message,
            default_key=SERVER_PRIVATE_KEY.fingerprints[0],
            clearsign=True
        )

    result = gpg.import_keys(public_key_in_str)
    encrypted_message = gpg.encrypt(str(message), result.fingerprints[0])

    return str(encrypted_message)


def encrypt_message(message: str, public_key_in_str: str) -> str:
    public_key = gpg.import_keys(public_key_in_str)

    return gpg.encrypt(message, public_key.fingerprints[0])
