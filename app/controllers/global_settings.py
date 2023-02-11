from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app import life_constants, logger
from app.models.global_settings import GlobalSettings

from app.schemas.admin import AdminSettingsModel
from app.schemas.global_settings import GlobalSettingsModel
from app.schemas.server import SettingsModel

__all__ = [
    "get_settings",
    "get_filled_settings",
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
    settings = GlobalSettings()

    db.add(settings)
    db.commit()

    return settings


def get_settings(db: Session, /) -> GlobalSettings:
    try:
        return db.query(GlobalSettings).one()
    except NoResultFound:
        return _create_settings(db)


def get_filled_settings(db: Session, /) -> GlobalSettingsModel:
    settings_instance = get_settings(db)
    settings = {}

    for life_constant_field_name in SETTINGS_FIELDS:
        field_name = life_constant_field_name.lower()

        if (value := getattr(settings_instance, field_name)) is not None:
            settings[field_name] = value
        else:
            settings[field_name] = getattr(life_constants, life_constant_field_name)

    return GlobalSettingsModel(**settings)


def get(db: Session, /, field: str):
    logger.info(f"Get Global Settings -> Get {field=}.")
    default_value = getattr(life_constants, field)

    if not life_constants.USE_GLOBAL_SETTINGS or field not in SETTINGS_FIELDS:
        logger.info(f"Get Global Settings -> Returning {default_value=}.")
        return default_value

    settings = get_settings(db)

    settings_field_name = field.lower()

    if (value := getattr(settings, settings_field_name)) is not None:
        logger.info(f"Get Global Settings -> Returning {value=}.")
        return value

    logger.info(f"Get Global Settings -> Returning {default_value=}.")
    return default_value


def update_settings(db: Session, /, update: AdminSettingsModel) -> GlobalSettings:
    settings = get_settings(db)

    for field, value in update.dict(exclude_unset=True).items():
        setattr(settings, field, value)

    logger.info(f"Request: Update Admin Settings -> Updated data. Committing to database.")
    db.add(settings)
    db.commit()
    db.refresh(settings)

    return settings
