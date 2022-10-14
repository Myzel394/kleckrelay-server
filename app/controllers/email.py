import secrets
from typing import Optional

from sqlalchemy.orm import Session

from app import logger
from app.authentication.errors import EmailIncorrectTokenError
from app.constants import (
    EMAIL_VERIFICATION_TOKEN_CHARS, EMAIL_VERIFICATION_TOKEN_LENGTH,
)
from app.mails.send_email_verification import send_email_verification
from app.models.email import Email
from app.utils import normalize_email

__all__ = [
    "create_email",
    "verify_email",
    "get_email_by_address",
    "send_verification_email",
]


def generate_token() -> str:
    return "".join(
        secrets.choice(EMAIL_VERIFICATION_TOKEN_CHARS)
        for _ in range(EMAIL_VERIFICATION_TOKEN_LENGTH)
    )


def send_verification_email(email: Email) -> None:
    send_email_verification(
        address=email.address,
        token=email.token,
    )


async def create_email(db: Session, /, address: str) -> Email:
    """Create a new email.

    Returns the email instance.

    Automatically sends the email to the user.
    """
    normalized_email = await normalize_email(address)

    logger.info(f"Create Email: Create email instance for {address}.")
    token = generate_token()

    email = Email(
        address=normalized_email,
        token=token,
    )

    db.add(email)
    db.commit()
    db.refresh(email)

    send_verification_email(email)

    logger.info(f"Create Email: {address} created successfully.")

    return email


def verify_email(db: Session, /, email: Email, token: str):
    logger.info(f"Verify email: Verifying {email.address}.")
    if email.is_verified:
        return

    if not email.token == token:
        logger.info(f"Verify email: Token for {email.address} is incorrect.")
        raise EmailIncorrectTokenError()

    logger.info(f"Verify email: Token for {email.address} is correct.")
    email.is_verified = True

    db.add(email)
    db.commit()
    db.refresh(email)
    logger.info(f"Verify email: {email.address} saved successfully.")


def get_email_by_address(db: Session, address: str) -> Optional[Email]:
    return db\
        .query(Email)\
        .filter_by(address=address)\
        .one()
