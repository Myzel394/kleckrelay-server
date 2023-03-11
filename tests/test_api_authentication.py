from datetime import datetime, timedelta

from starlette.testclient import TestClient

from app.models.enums.alias import AliasType
from app.models.enums.api_key import APIKeyScope


def test_can_authenticate_using_api_key(
    client: TestClient,
    create_user,
    create_api_key,
):
    user = create_user(is_verified=True)
    _, key = create_api_key(user=user, scopes=[APIKeyScope.ALIAS_CREATE])

    response = client.post(
        "/v1/alias/",
        headers={
            "Authorization": f"Api-Key {key}"
        },
        json={
            "type": AliasType.RANDOM,
        }
    )

    assert response.status_code == 200, f"Status code should be 200 but is {response.status_code}"


def test_can_not_authenticate_with_expired_api_key(
    client: TestClient,
    create_user,
    create_api_key,
):
    user = create_user(is_verified=True)
    _, key = create_api_key(
        user=user,
        scopes=[APIKeyScope.ALIAS_CREATE],
        expires_at=datetime.utcnow() - timedelta(days=1),
    )

    response = client.post(
        "/v1/alias/",
        headers={
            "Authorization": f"Api-Key {key}"
        },
        json={
            "type": AliasType.RANDOM,
        }
    )

    assert response.status_code == 401, f"Status code should be 401 but is {response.status_code}"


def test_can_not_authenticate_with_wrong_scope(
    client: TestClient,
    create_user,
    create_api_key,
):
    user = create_user(is_verified=True)
    _, key = create_api_key(user=user, scopes=[APIKeyScope.ALIAS_DELETE])

    response = client.post(
        "/v1/alias/",
        headers={
            "Authorization": f"Api-Key {key}"
        },
        json={
            "type": AliasType.RANDOM,
        }
    )

    assert response.status_code == 401, f"Status code should be 401 but is {response.status_code}"


def test_can_get_profile_without_preferences_with_missing_scope(
    client: TestClient,
    create_user,
    create_api_key,
):
    user = create_user(is_verified=True)
    _, key = create_api_key(user=user, scopes=[APIKeyScope.PROFILE_READ])

    response = client.get(
        "/v1/account/me/",
        headers={
            "Authorization": f"Api-Key {key}"
        },
    )

    assert response.status_code == 200, f"Status code should be 200 but is {response.status_code}"
    assert response.json().get("preferences") is None, "Preferences should be None"


def test_can_get_profile_with_preferences_with_correct_scope(
    client: TestClient,
    create_user,
    create_api_key,
) -> None:
    user = create_user(is_verified=True)
    _, key = create_api_key(
        user=user,
        scopes=[APIKeyScope.PROFILE_READ, APIKeyScope.PREFERENCES_READ]
    )

    response = client.get(
        "/v1/account/me/",
        headers={
            "Authorization": f"Api-Key {key}"
        },
    )

    assert response.status_code == 200, f"Status code should be 200 but is {response.status_code}"
    assert response.json()["preferences"] is not None, "Preferences should not be None"
