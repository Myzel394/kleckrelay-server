import base64

from pretty_bad_protocol import gnupg

from app import life_constants

__all__ = [
    "gpg"
]

gpg = gnupg.GPG()
gpg.encoding = "utf-8"

SERVER_PRIVATE_KEY = gpg.import_keys(base64.b64decode(life_constants.SERVER_PRIVATE_KEY))
