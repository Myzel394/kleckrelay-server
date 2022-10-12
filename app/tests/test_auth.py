from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app import life_constants
from app.models import User

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAm3pAntNs9dx+yhL/pkFQ
js4W6pCS0OSb837j/XHwkG1kRVVS+SxJRFqTL0vwe0sM7udjZpDIVQpmnNcJoZOQ
7Ra6r8rUPO3F18Ka4RvjJxiHIIRMcTDCXE4T5UzOuJnxfb4+tSvcNX2j7k6X+sGt
svuyFTmmSsMSNrNXRrbJKiFoViPgQhfOAPHTTdtzyfZLKQuKx7gmeuO1ehZ4QSvt
MMITv/aRCse3IIGAYGIvTXeCO7Qv7UUNBYUGsO+64BKHC24YA9j35zYXynnmXbZj
7+1E5J1/G1f5gL0CrlYA3l2Vh8ab+idalH8c3JusK+WkQ8QqdrrZTqeB+cglLb+E
ixU9WAqRfP292LWqq5tVPq9x226QzdrA422J9RcXXm22HqPayjYOzJdcabJshqna
MWef8MYIGhW2nGa1Mow38bM70RT9LmEoYHMuRTQeDKvbrObe6eoawDN9b3VYXQ2D
nHTLJN9ToaYtbRsDrf8pD2TCeUh8IDvad5aepf8bX+tkwT5xqQZODLfl4eriucWo
yYk4XUz9eiFyulyhc2wzLQgibs+Ml8xfoL4JrMpHLIEMlX/we190DIGlvtyqovCM
Il0PFeoiGtg/OT6KiPwHvOcS4owrV/Rc08fQWCYMK4pG6hArNt+htBPns/BYvTlU
xoXL4GatdKD+og4oHVMKmdUCAwEAAQ==
-----END PUBLIC KEY-----"""


def test_can_create_account_with_minimum_valid_data(
    db: Session,
    client: TestClient,
):
    response = client.post(
        "/auth/signup",
        json={
            "email": "email@example.com",
        }
    )
    assert response.status_code == 200, "Status code should be 200"


def test_can_create_account_with_valid_data_with_public_key(
    db: Session,
    client: TestClient,
):
    response = client.post(
        "/auth/signup",
        json={
            "email": "email@example.com",
            "public_key": PUBLIC_KEY,
        }
    )
    assert response.status_code == 200, "Status code should be 200"


def test_can_create_account_with_valid_data_with_all_data(
    db: Session,
    client: TestClient,
):
    response = client.post(
        "/auth/signup",
        json={
            "email": "email@example.com",
            "public_key": PUBLIC_KEY,
            "encrypted_private_key": "abc",
            "password": "abc",
        }
    )
    assert response.status_code == 200, "Status code should be 200"


def test_can_not_create_account_with_blocked_relays(
    db: Session,
    client: TestClient,
):
    life_constants.USER_EMAIL_ENABLE_OTHER_RELAYS = False
    response = client.post(
        "/auth/signup",
        json={
            "email": f"email@{life_constants.USER_EMAIL_OTHER_RELAY_DOMAINS[0]}"
        }
    )
    assert response.status_code == 422, "Status could should be 400"


def test_can_create_account_with_user_email_enable_other_relays_false(
        db: Session,
        client: TestClient,
):
    life_constants.USER_EMAIL_ENABLE_OTHER_RELAYS = False
    response = client.post(
        "/auth/signup",
        json={
            "email": f"email@example.com"
        }
    )
    assert response.status_code == 200, "Status could should be 200"


def test_can_verify_email_with_correct_token(
    create_user,
    client: TestClient,
):
    user: User = create_user()

    response = client.post(
        "/auth/verify-email",
        json={
            "email": user.email.address,
            "token": "abc",
        }
    )
    assert response.status_code == 200, "Status code should be 200"


def test_can_create_email_login_token(
    create_user,
    client: TestClient,
):
    user: User = create_user(is_verified=True)

    response = client.post(
        "/auth/login/email-token",
        json={
            "email": user.email.address,
        }
    )
    assert response.status_code == 200, "Status code should be 200"


def test_can_verify_login_token(
    create_user,
    create_email_token,
    client: TestClient,
):
    user: User = create_user(is_verified=True)
    email_login, token, same_request_token = create_email_token(user=user)

    response = client.post(
        "/auth/login/email-token/verify",
        json={
            "email": user.email.address,
            "token": token,
            "same_request_token": same_request_token,
        }
    )
    assert response.status_code == 200, "Status code should be 200"
