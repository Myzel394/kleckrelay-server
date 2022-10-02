from starlette.testclient import TestClient


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
