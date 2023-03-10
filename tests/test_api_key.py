from datetime import datetime, timedelta

from requests import Session
from starlette.testclient import TestClient


def test_can_create_api_key(
    client: TestClient,
    db: Session,
    create_user,
    create_auth_tokens,
) -> None:
    user = create_user(is_verified=True)
    auth = create_auth_tokens(user)

    response = client.post(
        "/v1/api-key/",
        json={
            "scopes": ["create:alias"],
            "label": "Test API Key",
        },
        headers=auth["headers"]
    )

    assert response.status_code == 200, f"Status code should be 200 but is {response.status_code}"
