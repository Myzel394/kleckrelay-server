from pretty_bad_protocol import gnupg

__all__ = [
    "gpg"
]

gpg = gnupg.GPG()
gpg.encoding = "utf-8"
