import pyotp
from starlette.testclient import TestClient

from app import constants
from app.models import User
from tests.helpers import is_a_jwt_token


def test_can_not_access_resource_when_otp_not_verified(
    create_user,
    setup_otp,
    create_email_token,
    client: TestClient,
):
    user: User = create_user(is_verified=True)
    setup_otp(user=user)
    email_login, token, same_request_token = create_email_token(user=user)

    response = client.post(
        "/v1/auth/login/email-token/verify",
        json={
            "email": user.email.address,
            "token": token,
            "same_request_token": same_request_token,
        }
    )
    assert response.status_code == 202, \
        f"Status code should be 202 but is {response.status_code}; Verifying email token."
    assert is_a_jwt_token(response.cookies[constants.ACCESS_TOKEN_COOKIE_NAME]), \
        "Access token should be a JWT token."

    response = client.get(
        "/v1/alias/",
        headers={
            "Authorization": f"Bearer {response.cookies[constants.ACCESS_TOKEN_COOKIE_NAME]}",
        }
    )
    assert response.status_code == 424, \
        f"Status code should be 424 but is {response.status_code}; Accessing resource without verified OTP."


def test_can_access_resource_when_otp_verified(
    create_user,
    create_auth_tokens,
    setup_otp,
    create_email_token,
    client: TestClient,
):
    user: User = create_user(is_verified=True)
    auth = create_auth_tokens(user=user)
    otp = setup_otp(user=user)
    email_login, token, same_request_token = create_email_token(user=user)

    response = client.post(
        "/v1/auth/login/email-token/verify",
        json={
            "email": user.email.address,
            "token": token,
            "same_request_token": same_request_token,
        }
    )
    assert response.status_code == 202, \
        f"Status code should be 202 but is {response.status_code}; Verifying email token."

    response = client.post(
        "/v1/auth/login/verify-otp",
        json={
            "code": pyotp.TOTP(otp.secret).now(),
            "cors_token": response.json()["cors_token"],
        },
        headers={
            "Authorization": f"Bearer {response.cookies[constants.ACCESS_TOKEN_COOKIE_NAME]}",
        }
    )

    assert response.status_code == 200, \
        f"Status code should be 200 but is {response.status_code}; Verifying OTP."

    response = client.get(
        "/v1/alias/",
        headers={
            "Authorization": f"Bearer {response.cookies[constants.ACCESS_TOKEN_COOKIE_NAME]}",
        }
    )

    assert response.status_code == 200, \
        f"Status code should be 200 but is " \
        f"{response.status_code}; Accessing resource without verified OTP."


def test_can_verify_otp(
    create_user,
    create_auth_tokens,
    create_email_token,
    setup_otp,
    client: TestClient,
):
    user = create_user()
    auth = create_auth_tokens(user=user)
    email_login, token, same_request_token = create_email_token(user=user)
    otp = setup_otp(user=user)

    response = client.post(
        "/v1/auth/login/email-token/verify",
        json={
            "email": user.email.address,
            "token": token,
            "same_request_token": same_request_token,
        }
    )
    assert response.status_code == 202, \
        "Status code should be 202; Verifying email login token failed"

    response = client.post(
        "/v1/auth/login/verify-otp",
        json={
            "code": pyotp.TOTP(otp.secret).now(),
            "cors_token": response.json()["cors_token"],
        },
        headers=auth["headers"],
    )

    assert response.status_code == 200, \
        f"Status code should be 200 but is {response.status_code}; Verifying OTP failed"
    assert is_a_jwt_token(response.cookies[constants.ACCESS_TOKEN_COOKIE_NAME]), \
        "Access token should be a JWT token"
    assert is_a_jwt_token(response.cookies[constants.REFRESH_TOKEN_COOKIE_NAME]), \
        "Refresh token should be a JWT token"


def test_can_not_verify_otp_with_incorrect_code(
    create_user,
    create_auth_tokens,
    create_email_token,
    setup_otp,
    client: TestClient,
):
    user = create_user()
    auth = create_auth_tokens(user=user)
    email_login, token, same_request_token = create_email_token(user=user)
    otp = setup_otp(user=user)

    response = client.post(
        "/v1/auth/login/email-token/verify",
        json={
            "email": user.email.address,
            "token": token,
            "same_request_token": same_request_token,
        }
    )
    assert response.status_code == 202, \
        "Status code should be 202; Verifying email login token failed"

    response = client.post(
        "/v1/auth/login/verify-otp",
        json={
            "code": str(int(pyotp.TOTP(otp.secret).now()) + 1),
            "cors_token": response.json()["cors_token"],
        },
        headers=auth["headers"],
    )

    assert response.status_code == 400, \
        f"Status code should be 200 but is {response.status_code}; Verifying OTP failed"
