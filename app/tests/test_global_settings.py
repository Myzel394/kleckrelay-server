from sqlalchemy.orm import Session
from starlette.testclient import TestClient

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


def test_can_get_settings(
    create_user,
    db: Session,
    client: TestClient,
    create_auth_tokens,
) -> None:
    user = create_user(is_verified=True, is_admin=True)
    auth = create_auth_tokens(user)

    response = client.get(
        "/v1/admin/settings/",
        headers=auth["headers"],
    )

    assert response.status_code == 200, f"Status code should be 200 but is {response.status_code}"


def test_can_update_settings(
    create_user,
    db: Session,
    client: TestClient,
    create_auth_tokens,
) -> None:
    user = create_user(is_verified=True, is_admin=True)
    auth = create_auth_tokens(user)
    settings = get_settings(db)

    settings.random_email_id_min_length = 20

    db.add(settings)
    db.commit()
    db.refresh(settings)

    response = client.patch(
        "/v1/admin/settings/",
        json={
            "random_email_id_min_length": 10,
        },
        headers=auth["headers"],
    )

    assert response.status_code == 200, f"Status code should be 200 but is {response.status_code}"
    assert response.json()["random_email_id_min_length"] == 10


def test_can_not_get_settings_when_disabled(
    create_user,
    create_auth_tokens,
    client: TestClient,
) -> None:
    life_constants.USE_GLOBAL_SETTINGS = False

    user = create_user(is_verified=True, is_admin=True)
    auth = create_auth_tokens(user)

    response = client.get(
        "/v1/admin/settings/",
        headers=auth["headers"],
    )

    assert response.status_code == 204, f"Status code should be 204 but is {response.status_code}"
