def test_can_create_account_with_valid_data(db, client):
    response = client.post(
        "/auth/signup",
        json={
            "email": "email@example.com",
        }
    )
    assert response.status_code == 200, "Status code should be 200"


def test_can_verify_email_with_correct_token(create_user, client,):
    user = create_user()

    response = client.post(
        "/auth/verify-email",
        json={
            "email": user.email.address,
            "token": "abc",
        }
    )
    assert response.status_code == 200, "Status code should be 200"


def test_can_create_email_login_token(create_user, client):
    user = create_user(is_verified=True)

    response = client.post(
        "/auth/login/email_token",
        json={
            "email": user.email.address,
        }
    )
    assert response.status_code == 200, "Status code should be 200"


def test_can_verify_login_token(create_user, create_email_token, client):
    user = create_user(is_verified=True)
    email_login, token, same_request_token = create_email_token(user=user)

    response = client.post(
        "/auth/login/email_token/verify",
        json={
            "email": user.email.address,
            "token": token,
            "same_request_token": same_request_token,
        }
    )
