from sqlalchemy.orm import Session

from app import logger
from app.models import User
from app.schemas.user import UserUpdate

__all__ = [
    "update_account_data",
]


def update_account_data(
    db: Session,
    /,
    user: User,
    data: UserUpdate,
) -> None:
    logger.info(f"Update account data: Updating account data for user {user.email.address}.")

    update_data = data.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(user, key, value)

    db.add(user)
    db.commit()
    db.refresh(user)
