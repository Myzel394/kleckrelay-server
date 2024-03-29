import pyotp
from starlette.testclient import TestClient


def test_can_do_otp_setup_flow(
    client: TestClient,
    create_user,
    create_auth_tokens
):
    user = create_user()
    auth = create_auth_tokens(user=user)

    response = client.post(
        "/v1/setup-otp",
        headers=auth["headers"],
    )

    assert response.status_code == 200, \
        f"Status code should be 200 but is {response.status_code}; Creating OTP failed"

    secret = response.json()["secret"]

    code = pyotp.TOTP(secret).now()

    response = client.post(
        "/v1/setup-otp/verify",
        headers=auth["headers"],
        json={
            "code": code,
        },
    )

    assert response.status_code == 200, \
        f"Status code should be 200 but is {response.status_code}; Verifying OTP failed"

    response = client.get(
        "/v1/setup-otp",
        headers=auth["headers"],
    )

    assert response.status_code == 200, \
        f"Status code should be 200 but is {response.status_code}; Getting OTP failed"
    assert response.json()["enabled"] is True, \
        "OTP should be enabled"


def test_can_verify_otp_with_old_code_after_recreating(
    client: TestClient,
    create_user,
    create_auth_tokens
):
    user = create_user()
    auth = create_auth_tokens(user=user)

    response = client.post(
        "/v1/setup-otp",
        headers=auth["headers"],
    )

    assert response.status_code == 200, \
        f"Status code should be 200 but is {response.status_code}; Creating OTP failed"

    secret = response.json()["secret"]

    code = pyotp.TOTP(secret).now()

    response = client.post(
        "/v1/setup-otp",
        headers=auth["headers"],
    )
    assert response.status_code == 200, \
        f"Status code should be 200 but is {response.status_code}; Recreating OTP failed"

    response = client.post(
        "/v1/setup-otp/verify",
        headers=auth["headers"],
        json={
            "code": code,
        },
    )

    assert response.status_code == 400, \
        f"Status code should be 400 but is {response.status_code}; Verifying OTP failed"


def test_can_not_verify_otp_with_incorrect_code(
    client: TestClient,
    create_user,
    create_auth_tokens,
):
    user = create_user()
    auth = create_auth_tokens(user=user)

    response = client.post(
        "/v1/setup-otp",
        headers=auth["headers"],
    )

    assert response.status_code == 200, \
        f"Status code should be 200 but is {response.status_code}; Creating OTP failed"

    secret = response.json()["secret"]

    code = pyotp.TOTP(secret).now()

    response = client.post(
        "/v1/setup-otp/verify",
        headers=auth["headers"],
        json={
            "code": "123456" if code != "123456" else "654321",
        },
    )

    assert response.status_code == 400, \
        f"Status code should be 400 but is {response.status_code}; Verifying OTP failed"


def test_can_recreate_otp_when_not_verified(
    create_user,
    create_auth_tokens,
    client: TestClient,
):
    user = create_user(is_verified=True)
    auth = create_auth_tokens(user=user)

    response = client.post(
        "/v1/setup-otp",
        headers=auth["headers"],
    )

    assert response.status_code == 200, \
        f"Status code should be 200 but is {response.status_code}; Creating OTP failed"

    response = client.post(
        "/v1/setup-otp",
        headers=auth["headers"],
    )

    assert response.status_code == 200, \
        f"Status code should be 200 but is {response.status_code}; Recreating OTP failed"


def test_can_not_recreate_otp_when_already_verified(
    create_user,
    create_auth_tokens,
    client: TestClient,
    setup_otp,
):
    user = create_user(is_verified=True)
    auth = create_auth_tokens(user=user)
    setup_otp(user=user)

    response = client.post(
        "/v1/setup-otp",
        headers=auth["headers"],
    )

    assert response.status_code == 424, \
        f"Status code should be 424 but is {response.status_code}; Recreating OTP failed"


def test_can_delete_otp_with_otp_code(
    create_user,
    create_auth_tokens,
    client: TestClient,
    setup_otp,
):
    user = create_user(is_verified=True)
    auth = create_auth_tokens(user=user)
    otp = setup_otp(user=user)

    response = client.request(
        "DELETE",
        "/v1/setup-otp",
        headers=auth["headers"],
        json={
            "code": pyotp.TOTP(otp.secret).now(),
        }
    )

    assert response.status_code == 200, \
        f"Status code should be 200 but is {response.status_code}; Deleting OTP failed"

    response = client.get(
        "/v1/setup-otp",
        headers=auth["headers"],
    )

    assert response.status_code == 200, \
        f"Status code should be 200 but is {response.status_code}; Getting OTP failed"
    assert response.json()["enabled"] is False, \
        "OTP should be disabled"


def test_can_delete_otp_with_recovery_code(
    create_user,
    create_auth_tokens,
    client: TestClient,
):
    user = create_user(is_verified=True)
    auth = create_auth_tokens(user=user)

    response = client.post(
        "/v1/setup-otp",
        headers=auth["headers"],
    )

    assert response.status_code == 200, \
        f"Status code should be 200 but is {response.status_code}; Creating OTP failed"

    recovery_code = response.json()["recovery_codes"][0]

    response = client.request(
        "DELETE",
        "/v1/setup-otp",
        json={
            "recovery_code": recovery_code.replace("-", ""),
        },
        headers=auth["headers"],
    )

    assert response.status_code == 200, \
        f"Status code should be 200 but is {response.status_code}; Deleting OTP failed"

    response = client.get(
        "/v1/setup-otp",
        headers=auth["headers"],
    )

    assert response.status_code == 200, \
        f"Status code should be 200 but is {response.status_code}; Getting OTP failed"
    assert response.json()["enabled"] is False, \
        "OTP should be disabled"


def test_can_not_delete_otp_with_invalid_otp_code(
        create_user,
        create_auth_tokens,
        client: TestClient,
):
    user = create_user(is_verified=True)
    auth = create_auth_tokens(user=user)

    response = client.post(
        "/v1/setup-otp",
        headers=auth["headers"],
    )

    assert response.status_code == 200, \
        f"Status code should be 200 but is {response.status_code}; Creating OTP failed"

    response = client.request(
        "DELETE",
        "/v1/setup-otp",
        json={
            "code": pyotp.TOTP("invalid").now(),
        },
        headers=auth["headers"],
    )

    assert response.status_code == 400, \
        f"Status code should be 400 but is {response.status_code}; Deleting OTP failed"


def test_can_not_delete_otp_with_invalid_recover_code(
    create_user,
    create_auth_tokens,
    client: TestClient,
):
    user = create_user(is_verified=True)
    auth = create_auth_tokens(user=user)

    response = client.post(
        "/v1/setup-otp",
        headers=auth["headers"],
    )

    assert response.status_code == 200, \
        f"Status code should be 200 but is {response.status_code}; Creating OTP failed"

    recovery_code = response.json()["recovery_codes"][0]

    response = client.request(
        "DELETE",
        "/v1/setup-otp",
        json={
            "recovery_code": recovery_code + "A",
        },
        headers=auth["headers"],
    )

    assert response.status_code == 400, \
        f"Status code should be 400 but is {response.status_code}; Deleting OTP failed"
