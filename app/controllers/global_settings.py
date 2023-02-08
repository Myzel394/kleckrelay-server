from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app import life_constants
from app.models.global_settings import GlobalSettings

__all__ = [
    "get_settings",
    "get"
]


def _get_changeable_constants() -> list[str]:
    fields = GlobalSettings.__table__.columns.keys()

    return [
        field.upper()
        for field in fields
        if field not in ("id", "created_at", "updated_at")
    ]


SETTINGS_FIELDS = _get_changeable_constants()


def _create_settings(db: Session, /) -> GlobalSettings:
    settings = GlobalSettings()

    db.add(settings)
    db.commit()

    return settings


def get_settings(db: Session, /) -> GlobalSettings:
    try:
        return db.query(GlobalSettings).one()
    except NoResultFound:
        return _create_settings(db)


def get(db: Session, /, field: str):
    default_value = getattr(life_constants, field)

    if not life_constants.USE_GLOBAL_SETTINGS or field not in SETTINGS_FIELDS:
        return default_value

    settings = get_settings(db)

    settings_field_name = field.lower()

    return getattr(settings, settings_field_name) or default_value
