from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app import life_constants, logger
from app.models.global_settings import GlobalSettings
from app.schemas.global_settings import GlobalSettingsModel

from app.schemas.server import SettingsModel

__all__ = [
    "get_settings",
    "get_settings_model",
    "get",
    "update_settings"
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
    settings = GlobalSettings(
        **{
            field.lower(): getattr(life_constants, field)
            for field in SETTINGS_FIELDS
        }
    )

    db.add(settings)
    db.commit()

    return settings


def get_settings(db: Session, /) -> GlobalSettings:
    try:
        return db.query(GlobalSettings).one()
    except NoResultFound:
        return _create_settings(db)


def get_settings_model(db: Session, /) -> GlobalSettingsModel:
    settings = get_settings(db)

    return GlobalSettingsModel(
        **{
            field.lower(): getattr(settings, field.lower())
            for field in SETTINGS_FIELDS
        }
    )


def get(db: Session, /, field: str):
    default_value = getattr(life_constants, field)

    if not life_constants.USE_GLOBAL_SETTINGS or field not in SETTINGS_FIELDS:
        return default_value

    settings = get_settings(db)

    settings_field_name = field.lower()

    if (value := getattr(settings, settings_field_name)) is not None:
        return value

    return default_value


def update_settings(db: Session, /, update: SettingsModel) -> GlobalSettings:
    settings = get_settings(db)

    for field, value in update.dict(exclude_unset=True, exclude_none=True).items():
        setattr(settings, field, value)

    logger.info(f"Request: Update Admin Settings -> Updated data. Committing to database.")
    db.add(settings)
    db.commit()
    db.refresh(settings)

    return settings
