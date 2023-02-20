from starlette.testclient import TestClient


def test_user_can_update_single_preferences(
    create_user,
    create_auth_tokens,
    create_random_alias,
    client: TestClient
):
    user = create_user(is_verified=True)
    auth = create_auth_tokens(user)

    other_alias = create_random_alias(user=user)

    response = client.patch(
        "/v1/preferences/",
        json={
            "alias_proxy_images": False,
        },
        headers=auth["headers"],
    )
    assert response.status_code == 200
    assert user.preferences.alias_proxy_images is False
    assert other_alias.pref_proxy_images is None
    assert other_alias.proxy_images is False


def test_user_can_update_single_preferences_with_instances_update(
    create_user,
    create_auth_tokens,
    create_random_alias,
    client: TestClient,
):
    user = create_user(is_verified=True)
    auth = create_auth_tokens(user)
    alias = create_random_alias(user=user, pref_proxy_images=True)

    assert user.email_aliases[0].pref_proxy_images is True
    response = client.patch(
        "/v1/preferences/",
        json={
            "alias_proxy_images": False,
            "update_all_instances": True,
        },
        headers=auth["headers"],
    )
    assert response.status_code == 200
    assert user.preferences.alias_proxy_images is False
    assert user.email_aliases[0].pref_proxy_images is False
