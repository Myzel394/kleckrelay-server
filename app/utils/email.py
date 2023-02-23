import email_normalize
from app import constants

__all__ = [
    "normalize_email",
    "is_local_a_bounce_address",
]


async def normalize_email(email: str) -> str:
    normalizer = email_normalize.Normalizer()

    return (await normalizer.normalize(email)).normalized_address


def is_local_a_bounce_address(local: str) -> bool:
    return any(
        alias.match(local)
        for alias in constants.FORBIDDEN_ALIASES
    )
