import email_normalize

__all__ = [
    "normalize_email"
]


async def normalize_email(email: str) -> str:
    normalizer = email_normalize.Normalizer()

    return (await normalizer.normalize(email)).normalized_address

