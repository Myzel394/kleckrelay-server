import uuid
from datetime import datetime, timedelta

from sqlalchemy import and_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.controllers.email import create_email, get_email_by_address
from app.controllers.user_preferences import create_user_preferences
from app.logger import logger
from app.models import Email
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils import normalize_email

from .global_settings import get

__all__ = [
    "check_if_email_exists",
    "get_user_by_email",
    "create_user",
    "get_user_by_id",
    "get_non_verified_users_to_delete",
    "delete_user"
]


async def check_if_email_exists(db: Session, /, email: str) -> bool:
    """Check if an email exists in the database."""
    try:
        await get_user_by_email(db, email)

        return True
    except NoResultFound:
        return False


async def get_user_by_email(db: Session, email: str) -> User:
    normalized_email = await normalize_email(email)

    return get_email_by_address(db, address=normalized_email).user


async def create_user(db: Session, /, user: UserCreate) -> User:
    """Create a new user to the database."""

    db_email = await create_email(db, address=user.email, language=user.language)
    preferences = create_user_preferences(db)

    logger.info(f"Create user: Creating user with email {db_email.address}.")

    db_user = User(
        email=db_email,
        preferences=preferences,
        public_key=user.public_key,
        encrypted_notes=user.encrypted_notes,
        language=user.language,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_email)

    logger.info(f"Create user: Created user {db_email.address} successfully. ID is: {db_user.id}.")

    return db_user


def get_user_by_id(db: Session, /, user_id: uuid.UUID) -> User:
    return db.query(User).filter_by(id=user_id).one()


def get_non_verified_users_to_delete(db: Session, /) -> list[User]:
    lifetime = get(db, "NON_VERIFIED_USER_LIFE_TIME_IN_DAYS")

    return db\
        .query(User)\
        .filter(
            and_(
                Email.is_verified is False,
                User.created_at < datetime.now() - timedelta(days=lifetime),
            )
        )\
        .all()


def delete_user(
    db: Session,
    /,
    user: User,
) -> None:
    db.delete(user)
    db.commit()
