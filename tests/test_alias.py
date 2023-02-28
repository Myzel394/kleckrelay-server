from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app import constants, life_constants
from app.models.alias import DeletedEmailAlias
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


def test_can_update_alias(
    client: TestClient,
    db: Session,
    create_user,
    create_auth_tokens,
    create_random_alias
) -> None:
    user = create_user(is_verified=True)
    auth = create_auth_tokens(user)
    alias = create_random_alias(user)

    response = client.patch(
        f"/v1/alias/{alias.id}",
        json={
            "is_active": False,
        },
        headers=auth["headers"]
    )

    assert response.status_code == 200, f"Status code should be 200 but is {response.status_code}"
    assert response.json()["is_active"] is False, "Returned alias should be inactive"
    assert alias.is_active is False, "Database alias should be inactive"


def test_can_not_delete_alias_by_default(
    client: TestClient,
    create_user,
    create_auth_tokens,
    create_random_alias
) -> None:
    user = create_user(is_verified=True)
    auth = create_auth_tokens(user)
    alias = create_random_alias(user)

    response = client.delete(
        f"/v1/alias/{alias.id}",
        headers=auth["headers"]
    )

    assert response.status_code == 403, f"Status code should be 403 but is {response.status_code}"


def test_can_delete_alias_if_deletion_is_enabled(
    client: TestClient,
    db: Session,
    create_user,
    create_auth_tokens,
    create_random_alias
) -> None:
    life_constants.ALLOW_ALIAS_DELETION = True
    user = create_user(is_verified=True)
    auth = create_auth_tokens(user)
    alias = create_random_alias(user)
    address = alias.address

    response = client.delete(
        f"/v1/alias/{alias.id}",
        headers=auth["headers"]
    )

    assert response.status_code == 200, f"Status code should be 200 but is {response.status_code}"
    deleted_alias = db.query(DeletedEmailAlias).one()
    assert deleted_alias.email == address, "Alias should be in deleted aliases table"


def test_can_not_surpass_max_amount(
    client: TestClient,
    create_user,
    create_auth_tokens,
    create_random_alias
):
    life_constants.MAX_ALIASES_PER_USER = 1

    user = create_user(is_verified=True)
    auth = create_auth_tokens(user)
    create_random_alias(user)

    response = client.post(
        "/v1/alias/",
        json={
            "type": AliasType.RANDOM,
        },
        headers=auth["headers"]
    )

    assert response.status_code == 403, f"Status code should be 403 but is {response.status_code}"
