from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.models.enums.alias import AliasType


def test_can_create_random_alias(
    client: TestClient,
    db: Session,
    create_user,
    create_auth_tokens,
) -> None:
    user = create_user(is_verified=True)
    auth = create_auth_tokens(user)

    response = client.post(
        "/v1/alias/",
        json={
            "type": AliasType.RANDOM,
        },
        headers=auth["headers"]
    )

    assert response.status_code == 200, f"Status code should be 200 but is {response.status_code}"


def test_can_not_create_random_alias_with_local(
    client: TestClient,
    db: Session,
    create_user,
    create_auth_tokens,
) -> None:
    user = create_user(is_verified=True)
    auth = create_auth_tokens(user)

    response = client.post(
        "/v1/alias/",
        json={
            "type": AliasType.RANDOM,
            "local": "test",
        },
        headers=auth["headers"]
    )

    assert response.status_code == 422, f"Status code should be 422 but is {response.status_code}"


def test_can_create_custom_alias(
    client: TestClient,
    db: Session,
    create_user,
    create_auth_tokens,
) -> None:
    user = create_user(is_verified=True)
    auth = create_auth_tokens(user)

    response = client.post(
        "/v1/alias/",
        json={
            "type": AliasType.CUSTOM,
            "local": "test",
        },
        headers=auth["headers"]
    )

    assert response.status_code == 200, f"Status code should be 200 but is {response.status_code}"
    assert response.json()["local"] != "test", "Local should have a suffix"


def test_can_not_create_custom_alias_without_local(
    client: TestClient,
    db: Session,
    create_user,
    create_auth_tokens,
) -> None:
    user = create_user(is_verified=True)
    auth = create_auth_tokens(user)

    response = client.post(
        "/v1/alias/",
        json={
            "type": AliasType.CUSTOM,
        },
        headers=auth["headers"]
    )

    assert response.status_code == 422, f"Status code should be 422 but is {response.status_code}"
