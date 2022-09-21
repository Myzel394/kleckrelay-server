from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.utils import normalize_email

__all__ = [
    "check_if_email_exists",
    "create_user",
]


def check_if_email_exists(db: Session, /, email: str) -> bool:
    """Check if an email exists in the database."""

    normalized_email = normalize_email(email)

    return db.query(User).filter(User.email == normalized_email).first() is not None


def create_user(db: Session, /, user: UserCreate) -> User:
    """Create a new user to the database."""

    db_user = User(
        email=user.email,
        encrypted_private_key=user.encrypted_private_key,
        public_key=user.public_key,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
