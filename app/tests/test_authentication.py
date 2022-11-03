from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app import constants, life_constants
from app.models import User
from app.tests.helpers import is_a_jwt_token

PUBLIC_KEY = """-----BEGIN PGP PUBLIC KEY BLOCK-----

xsBNBGNO6kcBCAC4Jl3YYGZSL5C57/otKDWujBo5Oz8isWY4NEGMgPEo7q+P
n8nUlFbh5pWMbNnXmhc86KhuCQjMkma8b8UEodlKAXoOxDkhMVEFP6ygWaFS
kMmG3e2K2TiQj3Vf+AibmsWtqJvq/kUSFFe9apP08cjMR2noSLc4sHM91HZq
AYn0XOjtRF8LPHcd/sUjUutO5MncqxxBWZxSIMMuy2xxtBqNbOaRjQmoXDiK
AEWhsQ3Q/I6PlnUOWc9k6pHrwpz5pRCQd9Yzo6N7sbinkbT/PxW8cJ9QqcNX
+qjhx7M/xNj/EHrATmUKGnS4Lskz2vWjAy8cq0R/X/T4QQHZzR3wDBSnABEB
AAHNHUpvaG4gU21pdGggPGpvaG5AZXhhbXBsZS5jb20+wsCKBBABCAA+BQJj
TupHBAsJBwgJEDAdaXsdpqWdAxUICgQWAAIBAhkBAhsDAh4BFiEEd0/AAnpp
odlZy7emMB1pex2mpZ0AAMhoCACGon5dP8cTZOLiwDg8AC4di1zjcIXuqlny
N4BWa0riR9CKIHkZ9yE2+UtQRq1041H9FiqO8xYXYM7Pabnno3oZtzCuAO3i
VIXVuHrLVgT6xkCq3rvSaESgy54EBCbBTEKWzlD5MTRRwZuwoIr03Tadrztu
HV2p58f6fgBl6AU7j3jRkNhHYBmtWzEFRVvFW/VIRfQhtkZwOLmGswJ27r73
BfpC+Fo/G+RLkMadJW4wMKQkXW6nhHpYE2DG/uwH0tlGdDD93vdlydGrfNKt
Zl1WeOSHrEsZE4Cu6RCND+5enXllBzMzMAZnVxbrBAeKH+X4LzzgomK5KSRJ
8UE0bsVbzsBNBGNO6kcBCADKyBvboWEnzlx/Hn7e5e3CipV7VAlqvaHHhoWY
ZMJOEOb0/WzuPqpSUiIPSX8t68MpM+JRAVXBJNrXVx6IK74XCxx1IpCgCwgx
wTu67KAviii6T4u9yQvOSiq1KZB60hep9Je7latfT4+Rn60LLJylKreeuUVD
4TOP3dzM1YtVz0P/f7sHGBVBUmyeuJF/qqLhj2BMen7m6R1XkmPveJRodTVD
K/4Vb7bp7eGngjWtujcljwFPhnpCLaQDomDkO0Wn+X2sgtUFGg15qte/eeqQ
V6RyehO4Jwyg/db5KlyzLGNqjhkaRC+ggHAWdanaSRUhsQdqy7mkOpivB70S
3Ff9ABEBAAHCwHYEGAEIACoFAmNO6kcJEDAdaXsdpqWdAhsMFiEEd0/AAnpp
odlZy7emMB1pex2mpZ0AAJboB/9xOQbp1xIJOyzCLIx0gCVC2FBczfw28Tm3
XQAIhhibh4qhtMYc98x6RwRudBpF/+CxIvhFQmrdBcZIRu84uRMxtLahZxSk
x0af7kbi+R7RmC7MpRxedhS3hxlCN3tfmXnbSBOUSxYlT8po1ecMBdxmVADQ
E+VhWnXe16i8EFvYK5o8N10Ec9AOLETETPUSw57UQ6hXk6LCy9kANopwaTSD
Je0/exrSMrLLebXnR6mN4TLDgCEwuNoT3aHkxqKXWIlsekj+bJeu8qf8tYHx
BCApP+r4epdoEU2tE3tkiiVpqY2rV/Go2E6EQVGmJFTkO4919f7J3LWONh9p
wQ4pBgRf
=XPl4
-----END PGP PUBLIC KEY BLOCK-----"""


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
            "encrypted_notes": "abc",
        }
    )
    assert response.status_code == 200, "Status code should be 200"


def test_can_not_create_account_with_invalid_public_key(
    db: Session,
    client: TestClient,
):
    response = client.post(
        "/auth/signup",
        json={
            "email": "email@example.com",
            "public_key": """-----BEGIN PGP PUBLIC KEY BLOCK-----

-----END PGP PUBLIC KEY BLOCK-----""",
            "encrypted_notes": "abc",
        }
    )
    assert response.status_code == 422, "Status code should be 422"


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
    assert is_a_jwt_token(response.cookies[constants.ACCESS_TOKEN_COOKIE_NAME]), \
        f"Cookie {constants.ACCESS_TOKEN_COOKIE_NAME} should be a jwt token."
    assert is_a_jwt_token(response.cookies[constants.REFRESH_TOKEN_COOKIE_NAME]), \
        f"Cookie {constants.REFRESH_TOKEN_COOKIE_NAME} should be a jwt token."


def test_can_verify_email_again(
    create_user,
    client: TestClient,
):
    user: User = create_user(is_verified=True)

    response = client.post(
        "/auth/verify-email",
        json={
            "email": user.email.address,
            "token": "abc",
        }
    )
    assert response.status_code == 202, "Status code should be 200"
    assert response.cookies.get(constants.ACCESS_TOKEN_COOKIE_NAME, default=None) is None, \
        f"Cookie {constants.ACCESS_TOKEN_COOKIE_NAME} should not be set."
    assert response.cookies.get(constants.REFRESH_TOKEN_COOKIE_NAME, default=None) is None, \
        f"Cookie {constants.REFRESH_TOKEN_COOKIE_NAME} should not be set."


def test_can_resend_email(
    create_user,
    client: TestClient,
):
    user: User = create_user()

    response = client.post(
        "/auth/resend-email",
        json={
            "email": user.email.address,
        }
    )
    assert response.status_code == 200, "Status code should be 200"


def test_resend_email_with_invalid_email_returns_error(
    create_user,
    client: TestClient,
):
    user: User = create_user()

    response = client.post(
        "/auth/resend-email",
        json={
            "email": "abc" + user.email.address,
        }
    )
    assert response.status_code == 404, "Status code should be 404"


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


def test_can_verify_login_token_using_different_device(
    create_user,
    create_email_token,
    client: TestClient,
):
    user: User = create_user(is_verified=True)
    email_login, token, same_request_token = create_email_token(user=user)

    response = client.patch(
        "auth/login/email-token/allow-login-from-different-devices",
        json={
            "email": user.email.address,
            "same_request_token": same_request_token,
            "allow": True,
        }
    )
    assert response.status_code == 200, "Status code for allowing login from different " \
                                        "devices should be 200"

    response = client.post(
        "/auth/login/email-token/verify",
        json={
            "email": user.email.address,
            "token": token,
        }
    )
    assert response.status_code == 200, "Status code for verifying email login token should be 200"


def test_can_not_verify_login_token_using_different_device_when_not_available(
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
        }
    )
    assert response.status_code == 400, "Status code should be 400"


def test_can_resend_valid_email_verification_code(
    create_user,
    create_email_token,
    client: TestClient,
):
    user: User = create_user(is_verified=True)
    email_login, token, same_request_token = create_email_token(user=user)

    response = client.post(
        "/auth/login/email-token/resend-email",
        json={
            "email": user.email.address,
            "same_request_token": same_request_token,
        }
    )
    assert response.status_code == 200, "Status code should be 200"


def test_can_not_resend_email_verification_code_with_invalid_email(
        create_user,
        create_email_token,
        client: TestClient,
):
    user: User = create_user(is_verified=True)
    email_login, token, same_request_token = create_email_token(user=user)

    response = client.post(
        "/auth/login/email-token/resend-email",
        json={
            "email": "a" + user.email.address,
            "same_request_token": same_request_token,
        }
    )
    assert response.status_code == 404, "Status code should be 404"


def test_can_not_resend_email_verification_code_with_invalid_same_request_token(
        create_user,
        create_email_token,
        client: TestClient,
):
    user: User = create_user(is_verified=True)
    email_login, token, same_request_token = create_email_token(user=user)

    response = client.post(
        "/auth/login/email-token/resend-email",
        json={
            "email": "a" + user.email.address,
            "same_request_token": "a" * len(same_request_token)
        }
    )
    assert response.status_code == 404, "Status code should be 404"
