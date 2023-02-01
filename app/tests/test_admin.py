from starlette.testclient import TestClient


def test_admin_can_get_correct_admin_users(
    create_user,
    client: TestClient,
    create_auth_tokens,
):
    user = create_user(is_verified=True, is_admin=True)
    non_admin = create_user(is_verified=False)
    auth = create_auth_tokens(user)

    response = client.get(
        "/v1/admin/get-user-admins/",
        headers=auth["headers"],
    )

    assert response.status_code == 200, f"Status code should be 200 but is {response.status_code}"

    assert len(response.json()["users"]) == 1, "There should be only one admin user."
    assert str(response.json()["users"][0]["id"]) == str(user.id), \
        "Admin user should be in the response."
