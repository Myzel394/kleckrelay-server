from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.authentication.errors import EmailIncorrectTokenError
from app.models.email import Email
from app.utils import hash_slowly

__all__ = [
    "verify_email",
    "get_email_by_address",
]


def verify_email(db: Session, /, email: Email, token: str):
    if email.is_verified:
        return

    if not email.hashed_token == hash_slowly(token):
        raise EmailIncorrectTokenError()

    email.verified_at = datetime.utcnow()

    db.add(email)
    db.commit()
    db.refresh(email)


def get_email_by_address(db: Session, address: str) -> Optional[Email]:
    return db.query(Email).filter(Email.address == address).first()
