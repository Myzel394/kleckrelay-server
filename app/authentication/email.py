import secrets
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.authentication.errors import EmailIncorrectTokenError
from app.constants import EMAIL_VERIFICATION_TOKEN_CHARS, EMAIL_VERIFICATION_TOKEN_LENGTH
from app.mails.send_email_verification import send_email_verification
from app.models.email import Email
from app.utils import hash_slowly

__all__ = [
    "create_email",
    "verify_email",
    "get_email_by_address",
]


def generate_token() -> str:
    return "".join(
        secrets.choice(EMAIL_VERIFICATION_TOKEN_CHARS)
        for _ in range(EMAIL_VERIFICATION_TOKEN_LENGTH)
    )


def create_email(db: Session, /, address: str) -> Email:
    """Create a new email.

    Returns the email instance.

    Automatically sends the email to the user.
    """

    token = generate_token()

    email = Email(
        address=address,
        token=token,
    )

    db.add(email)
    db.commit()
    db.refresh(email)

    send_email_verification(
        address=address,
        token=token,
    )

    return email


def verify_email(db: Session, /, email: Email, token: str):
    if email.is_verified:
        return

    if not email.token == token:
        raise EmailIncorrectTokenError()

    email.verified_at = datetime.utcnow()

    db.add(email)
    db.commit()
    db.refresh(email)


def get_email_by_address(db: Session, address: str) -> Optional[Email]:
    return db.query(Email).filter(Email.address == address).first()
