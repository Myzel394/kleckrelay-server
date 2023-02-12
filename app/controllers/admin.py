from sqlalchemy.orm import Session

from app import life_constants
from app.models import Email, User

__all__ = [
    "get_admin_users",
]


def get_admin_users(db: Session, /) -> list[User]:
    return (
        db.query(User)
        .join(Email)
        .filter(Email.address.in_(life_constants.ADMINS))
        .all()
    )
