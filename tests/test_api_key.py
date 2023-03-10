from datetime import datetime, timedelta

from requests import Session
from starlette.testclient import TestClient

from app.models.enums.api_key import APIKeyScope


def test_can_create_api_key(
    client: TestClient,
    db: Session,
    create_user,
    create_auth_tokens,
) -> None:
    user = create_user(is_verified=True)
    auth = create_auth_tokens(user)

    response = client.post(
        "/v1/api-key/",
        json={
            "scopes": ["create:alias"],
            "label": "Test API Key",
        },
        headers=auth["headers"]
    )

    assert response.status_code == 200, f"Status code should be 200 but is {response.status_code}"


def test_can_delete_api_key_by_id(
    client: TestClient,
    create_user,
    create_api_key,
    create_auth_tokens,
):
    user = create_user(is_verified=True)
    auth = create_auth_tokens(user)
    api_key, _ = create_api_key(
        user=user,
        scopes=[APIKeyScope.ALIAS_CREATE],
        expires_at=datetime.utcnow() - timedelta(days=1),
    )

    response = client.delete(
        f"/v1/api-key/{api_key.id}/",
        headers=auth["headers"]
    )

    assert response.status_code == 200, f"Status code should be 200 but is {response.status_code}"


def test_can_delete_api_key_by_key(
    client: TestClient,
    create_user,
    create_api_key,
):
    user = create_user(is_verified=True)
    _, key = create_api_key(
        user=user,
        scopes=[APIKeyScope.ALIAS_CREATE],
        expires_at=datetime.utcnow() + timedelta(days=1),
    )

    response = client.request(
        "DELETE",
        "/v1/api-key/",
        json={
            "key": key,
        }
    )

    assert response.status_code == 200, f"Status code should be 200 but is {response.status_code}"


def test_can_get_api_keys(
    client: TestClient,
    create_user,
    create_api_key,
    create_auth_tokens,
):
    user = create_user(is_verified=True)
    auth = create_auth_tokens(user)
    create_api_key(
        user=user,
        scopes=[APIKeyScope.ALIAS_CREATE],
        expires_at=datetime.utcnow() + timedelta(days=1),
    )

    response = client.get(
        "/v1/api-key/",
        headers=auth["headers"]
    )

    assert response.status_code == 200, f"Status code should be 200 but is {response.status_code}"
    assert len(response.json()["items"]) == 1, "There should be one API key"
