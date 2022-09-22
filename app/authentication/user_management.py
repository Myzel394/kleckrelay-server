from typing import Optional

from sqlalchemy.orm import Session

from app.authentication.email import create_email, get_email_by_address
from app.models.email import Email
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils import normalize_email

__all__ = [
    "check_if_email_exists",
    "get_user_by_email",
    "create_user",
]


async def check_if_email_exists(db: Session, /, email: str) -> bool:
    """Check if an email exists in the database."""
    return (await get_user_by_email(db, email)) is not None


async def get_user_by_email(db: Session, email: str) -> Optional[User]:
    normalized_email = await normalize_email(email)

    email_instance = get_email_by_address(db, address=normalized_email)

    if email_instance is None:
        return None

    return email_instance.user


def create_user(db: Session, /, user: UserCreate) -> User:
    """Create a new user to the database."""

    db_email = create_email(db, address=user.email)

    db_user = User(
        email=db_email,
        encrypted_password=user.encrypted_password,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
