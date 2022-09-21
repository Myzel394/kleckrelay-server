import email_normalize

__all__ = [
    "normalize_email",
    "hash_slowly",
    "hash_fast",
]


def normalize_email(email: str) -> str:
    return email_normalize.normalize(email).normalized_address


def hash_slowly(value: str) -> str:
    ...


def hash_fast(value: str) -> str:
    ...
