from sqlalchemy.orm import Session

from app import life_constants
from app.controllers.global_settings import get_settings, get


def test_can_get_global_setting_if_enabled_and_value_not_null(
    db: Session,
) -> None:
    life_constants.USE_GLOBAL_SETTINGS = True

    settings = get_settings(db)

    settings.random_email_id_min_length = 20

    db.add(settings)
    db.commit()
    db.refresh(settings)

    new_value = get(db, "RANDOM_EMAIL_ID_MIN_LENGTH")

    assert new_value == 20


def test_can_get_life_constant_when_global_setting_is_null(
    db: Session,
) -> None:
    life_constants.USE_GLOBAL_SETTINGS = True

    settings = get_settings(db)

    settings.random_email_id_min_length = None

    db.add(settings)
    db.commit()
    db.refresh(settings)

    new_value = get(db, "RANDOM_EMAIL_ID_MIN_LENGTH")

    assert new_value == life_constants.RANDOM_EMAIL_ID_MIN_LENGTH
