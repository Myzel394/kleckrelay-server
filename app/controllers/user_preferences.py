from sqlalchemy.orm import Session

from app import logger
from app.models import EmailAlias, UserPreferences
from app.schemas.user_preferences import UserPreferencesUpdate

__all__ = [
    "create_user_preferences",
    "update_user_preferences",
]


def create_user_preferences(db: Session, /) -> UserPreferences:
    preferences = UserPreferences()

    db.add(preferences)
    db.commit()
    db.refresh(preferences)

    return preferences


def update_user_preferences(
    db: Session,
    /,
    preferences: UserPreferences,
    update: UserPreferencesUpdate,
) -> None:
    logger.info(f"Update user preferences: Updating user preferences.")

    user = preferences.user

    update_data = update.dict(exclude_unset=True)
    update_all = update_data.pop("update_all_instances", None)

    for key, value in update_data.items():
        setattr(user.preferences, key, value)

    db.add(user.preferences)
    db.commit()
    db.refresh(user.preferences)

    if update_all:
        update_fields = {
            name.split("_", 1)[1]: value
            for name, value in update_data.items()
            if value is not None
        }
        aliases = db.query(EmailAlias).filter_by(user_id=user.id).all()

        for alias in aliases:
            for key, value in update_fields.items():
                setattr(alias, f"pref_{key}", value)

            # Bulk update does not work
            db.add(alias)
            db.commit()
            db.refresh(alias)
