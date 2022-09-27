from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.constants import IS_TESTING
from app.controllers.email import create_email, get_email_by_address
from app.logger import logger
from app.models.user import User
from app.schemas.user import UserCreate
from app.tests.variables import VARIABLES
from app.utils import normalize_email

__all__ = [
    "check_if_email_exists",
    "get_user_by_email",
    "create_user",
    "get_user_by_id",
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


async def create_user(db: Session, /, user: UserCreate) -> User:
    """Create a new user to the database."""

    db_email = await create_email(db, address=user.email)

    logger.info(f"Create user: Creating user with email {db_email.address}.")

    db_user = User(
        email=db_email,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    logger.info(f"Create user: Created user {db_email.address} successfully. ID is: {db_user.id}.")

    return db_user


def get_user_by_id(db: Session, /, user_id: str) -> User:
    if (user := db.query(User).filter(User.id == UUID(user_id)).first()) is not None:
        return user

    raise HTTPException(
        status_code=400,
        detail="User account not found."
    )
