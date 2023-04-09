import base64

from starlette.testclient import TestClient


PUBLIC_KEY = """-----BEGIN PGP PUBLIC KEY BLOCK-----

xjMEY1BWURYJKwYBBAHaRw8BAQdAF7V3c/or1pqMSO+K1NdlTzX8M3OWMIsM
fRaXjBpKcfrNG0pvbiBTbWl0aCA8am9uQGV4YW1wbGUuY29tPsKMBBAWCgA+
BQJjUFZRBAsJBwgJEPYcYW9Bd+RzAxUICgQWAAIBAhkBAhsDAh4BFiEEoXES
0EdOGluYpuHr9hxhb0F35HMAAHPbAQDKUYRKK4fBmx0oY51NFngIWlgh37r2
jh43FGyEfPtiiAD/ar4x4hYdzdTgstCd5IgHGN0rHePn8buFQ+BTclK3UwjO
OARjUFZREgorBgEEAZdVAQUBAQdAfNbp3wadPhBZd8PA0RuQbsWLQMkKozDF
x/vu1H34bQQDAQgHwngEGBYIACoFAmNQVlEJEPYcYW9Bd+RzAhsMFiEEoXES
0EdOGluYpuHr9hxhb0F35HMAAPaXAP90baEdk1ughlSfxwr1/qdXYasj4eXD
CY/XrzMgKvnwawEAtMHyvho1Les1B+7jJsKpNmOjssHIbDSeWTc0Dl8hugc=
=/9/F
-----END PGP PUBLIC KEY BLOCK-----"""


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


def test_can_update_gpg_key_preference(
    create_user,
    create_auth_tokens,
    client: TestClient,
) -> None:
    user = create_user(is_verified=True)
    auth = create_auth_tokens(user)

    response = client.patch(
        "/v1/preferences/",
        json={
            "email_gpg_public_key": PUBLIC_KEY,
        },
        headers=auth["headers"],
    )
    print(response.json())

    assert response.status_code == 200


def test_can_not_update_preferences_with_invalid_public_key(
    create_user,
    create_auth_tokens,
    client: TestClient,
) -> None:
    user = create_user(is_verified=True)
    auth = create_auth_tokens(user)

    invalid_public_key = """-----BEGIN PGP PUBLIC KEY BLOCK-----
Not a valid public key
-----END PGP PUBLIC KEY BLOCK-----"""

    response = client.patch(
        "/v1/preferences/",
        json={
            "email_gpg_public_key": invalid_public_key,
        },
        headers=auth["headers"],
    )

    assert response.status_code == 422


def test_can_find_public_key(
    create_user,
    create_auth_tokens,
    client: TestClient,
):
    # "proton.me" strangely gives for every email address a public key
    email = "no-reply@protonmail.com"

    user = create_user(is_verified=True, email=email)
    auth = create_auth_tokens(user)

    response = client.post(
        "/v1/preferences/find-public-key",
        headers=auth["headers"],
    )

    assert response.status_code == 200
    assert response.json()["public_key"] is not None


def test_can_not_find_public_key_for_nonexistent_mail(
    create_user,
    create_auth_tokens,
    client: TestClient,
):
    # Please do not register this email just to fuck up our tests
    # We base64 encode it so that bots don't register the domain
    email = base64.b64decode(
        "c2FoY3lpeGl1YnV2aWZk"
        "aGlqYnNoem"
        "5mdWhiY2l2eEBkb25vdHJlZ2lzdGVydGhpc2RvbWFpbnV"
        "pamFzaWRta256anVma2hhc2RmaGp2eGNuaGp1eXhuY3YuY29t"
    )

    user = create_user(is_verified=True, email=email)
    auth = create_auth_tokens(user)

    response = client.post(
        "/v1/preferences/find-public-key",
        headers=auth["headers"],
    )

    assert response.status_code == 404
