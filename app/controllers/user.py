from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.controllers.email import create_email, get_email_by_address
from app.life_constants import USER_PASSWORD_HASH_SALT
from app.logger import logger
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils import hash_slowly, normalize_email

__all__ = [
    "check_if_email_exists",
    "get_user_by_email",
    "create_user",
    "get_user_by_id",
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

    db_email = await create_email(db, address=user.email)

    logger.info(f"Create user: Creating user with email {db_email.address}.")

    password = f"{user.password}:{USER_PASSWORD_HASH_SALT}" if user.password is not None else None

    db_user = User(
        email=db_email,
        hashed_password=hash_slowly(password) if password is not None else None,
        public_key=user.public_key,
        encrypted_private_key=user.encrypted_private_key,
    )

    db.add(db_user)
    db.add(db_email)
    db.commit()
    db.refresh(db_email)

    logger.info(f"Create user: Created user {db_email.address} successfully. ID is: {db_user.id}.")

    return db_user


def get_user_by_id(db: Session, /, user_id: str) -> User:
    try:
        return db.query(User).filter(User.id == UUID(user_id)).one()
    except NoResultFound:
        raise HTTPException(
            status_code=401,
            detail="User account not found."
        )
