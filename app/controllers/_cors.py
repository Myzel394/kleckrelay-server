import secrets

from app.constants import CORS_TOKEN_CHARS, CORS_TOKEN_LENGTH

__all__ = [
    "generate_cors_token"
]


def generate_cors_token() -> str:
    return "".join(
        secrets.choice(CORS_TOKEN_CHARS)
        for _ in range(CORS_TOKEN_LENGTH)
    )
