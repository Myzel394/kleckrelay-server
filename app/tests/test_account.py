from starlette.testclient import TestClient

from app.utils import verify_slow_hash


def test_verify_password_works_correctly(
    create_user,
    create_auth_tokens,
    client: TestClient,
):
    user = create_user(is_verified=True, password="test")
    auth = create_auth_tokens(user)

    response = client.post(
        "/account/verify-password",
        json={
            "password": "test",
        },
        headers=auth["headers"],
    )
    assert response.status_code == 200, "Status code should be 200"
    assert response.json()["is_password_correct"] is True, "Password should be correct"


def test_verify_password_does_not_work_for_invalid_passwords(
    create_user,
    create_auth_tokens,
    client: TestClient,
):
    user = create_user(is_verified=True, password="test")
    auth = create_auth_tokens(user)

    response = client.post(
        "/account/verify-password",
        json={
            "password": "test1",
        },
        headers=auth["headers"],
    )
    assert response.status_code == 200, "Status code should be 200"
    assert response.json()["is_password_correct"] is False, "Password should NOT be correct"


def test_can_update_account(
    create_user,
    create_auth_tokens,
    client: TestClient,
):
    user = create_user(is_verified=True, password="test")
    auth = create_auth_tokens(user)

    assert verify_slow_hash(user.hashed_password, "test") is True, \
        "Verification of initial password should work."

    response = client.patch(
        "/account/",
        json={
            "password": "new-password"
        },
        headers=auth["headers"],
    )
    assert response.status_code == 200, "Status code should be 200"
    assert verify_slow_hash(user.hashed_password, "new-password") is True, \
        "Verification of new password should work."

