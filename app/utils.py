import email_normalize

__all__ = [
    "normalize_email"
]


def normalize_email(email: str) -> str:
    return email_normalize.normalize(email).normalized_address
