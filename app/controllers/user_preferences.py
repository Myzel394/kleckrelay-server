from sqlalchemy.orm import Session

from app.models import UserPreferences

__all__ = [
    "create_user_preferences",
]


def create_user_preferences(db: Session, /) -> UserPreferences:
    preferences = UserPreferences()

    db.add(preferences)
    db.commit()
    db.refresh(preferences)

    return preferences
