from starlette.testclient import TestClient


def test_can_get_reserved_alias(
    create_user,
    create_reserved_alias,
    create_auth_tokens,
    db,
    client: TestClient,
) -> None:
    user = create_user(is_verified=True, is_admin=True)
    auth = create_auth_tokens(user)

    response = client.get("/v1/reserved-alias/", headers=auth["headers"])

    assert response.status_code == 200, f"Status code should be 200 but is {response.status_code}"


def test_can_create_reserved_alias(
    create_user,
    create_auth_tokens,
    db,
    client: TestClient,
) -> None:
    user = create_user(is_verified=True, is_admin=True)
    auth = create_auth_tokens(user)

    assert user.is_admin is True, "User should be an admin."

    response = client.post(
        "/v1/reserved-alias/",
        json={
            "local": "something",
            "users": [
                {
                    "id": str(user.id),
                }
            ]
        },
        headers=auth["headers"],
    )

    assert response.status_code == 200, f"Status code should be 200 but is {response.status_code}"

    # Test can not create another reserved alias

    response = client.post(
        "/v1/reserved-alias/",
        json={
            "local": "something",
            "users": [
                {
                    "id": str(user.id),
                }
            ]
        },
        headers=auth["headers"],
    )

    assert response.status_code == 400, f"Status code should be 400 but is {response.status_code}"


def test_can_not_create_reserved_alias_with_no_users(
    create_user,
    create_auth_tokens,
    db,
    client: TestClient,
) -> None:
    user = create_user(is_verified=True, is_admin=True)
    auth = create_auth_tokens(user)

    response = client.post(
        "/v1/reserved-alias/",
        json={
            "local": "something",
            "users": []
        },
        headers=auth["headers"],
    )

    assert response.status_code == 422, f"Status code should be 422 but is {response.status_code}"


def test_can_not_create_reserved_alias_with_no_admin_user_as_users(
    create_user,
    create_auth_tokens,
    db,
    client: TestClient,
) -> None:
    user = create_user(is_verified=True, is_admin=True)
    auth = create_auth_tokens(user)
    no_admin_user = create_user(is_verified=True)

    response = client.post(
        "/v1/reserved-alias/",
        json={
            "local": "something",
            "users": [
                {
                    "id": str(no_admin_user.id)
                }
            ]
        },
        headers=auth["headers"],
    )

    assert response.status_code == 400, f"Status code should be 400 but is {response.status_code}"


def test_can_not_create_reserved_alias_with_no_admin_user(
    create_user,
    create_auth_tokens,
    db,
    client: TestClient,
) -> None:
    user = create_user(is_verified=True, is_admin=True)
    no_admin_user = create_user(is_verified=True)
    auth = create_auth_tokens(no_admin_user)

    response = client.post(
        "/v1/reserved-alias/",
        json={
            "local": "something",
            "users": [
                {
                    "id": str(user.id)
                }
            ]
        },
        headers=auth["headers"],
    )

    assert response.status_code == 401, f"Status code should be 401 but is {response.status_code}"


def test_can_update_alias(
    create_user,
    create_reserved_alias,
    create_auth_tokens,
    db,
    client: TestClient,
) -> None:
    user = create_user(is_verified=True, is_admin=True)
    auth = create_auth_tokens(user)
    alias = create_reserved_alias(users=[user])

    response = client.patch(
        f"/v1/reserved-alias/{alias.id}",
        json={
            "users": [
                {
                    "id": str(user.id)
                }
            ]
        },
        headers=auth["headers"],
    )

    assert response.status_code == 200, f"Status code should be 200 but is {response.status_code}"


def test_can_not_update_alias_when_users_are_empty(
    create_user,
    create_reserved_alias,
    create_auth_tokens,
    db,
    client: TestClient,
) -> None:
    user = create_user(is_verified=True, is_admin=True)
    auth = create_auth_tokens(user)
    alias = create_reserved_alias(users=[user])

    response = client.patch(
        f"/v1/reserved-alias/{alias.id}",
        json={
            "users": []
        },
        headers=auth["headers"],
    )

    assert response.status_code == 422, f"Status code should be 422 but is {response.status_code}"


def test_can_not_update_alias_when_users_are_not_admin(
    create_user,
    create_reserved_alias,
    create_auth_tokens,
    db,
    client: TestClient,
) -> None:
    user = create_user(is_verified=True, is_admin=True)
    not_admin = create_user(is_verified=True)
    auth = create_auth_tokens(user)
    alias = create_reserved_alias(users=[user])

    response = client.patch(
        f"/v1/reserved-alias/{alias.id}",
        json={
            "users": [
                {
                    "id": str(not_admin.id)
                }
            ]
        },
        headers=auth["headers"],
    )

    assert response.status_code == 400, f"Status code should be 400 but is {response.status_code}"


def test_can_not_create_forbidden_alias(
    create_user,
    create_auth_tokens,
    db,
    client: TestClient,
) -> None:
    user = create_user(is_verified=True, is_admin=True)
    auth = create_auth_tokens(user)

    response = client.post(
        "/v1/reserved-alias/",
        json={
            "local": "bounce",
            "users": [
                {
                    "id": str(user.id),
                }
            ]
        },
        headers=auth["headers"],
    )

    assert response.status_code == 422, f"Status code should be 422 but is {response.status_code}"
