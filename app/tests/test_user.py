from .main import client
from .variables import VARIABLES
from app.database.base import SessionLocal
from app.models import Email


def test_can_create_account_with_valid_data():
    response = client.post(
        "/auth/signup",
        json={
            "email": "user@example.com",
        }
    )
    print(response)
    print(VARIABLES)
