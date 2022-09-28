import json
import uuid

import pytest
from starlette.testclient import TestClient

from .helpers import create_item
from app.models import Email
from app.schemas.email import Email as EmailSchema
from .test_database import override_get_db


def test_can_create_account_with_valid_data(db, client):
    response = client.post(
        "/auth/signup",
        json={
            "email": "email@example.com",
        }
    )
    assert response.status_code == 200, "Status code should be 200"


def test_can_verify_email_with_correct_token(user, client,):
    response = client.post(
        "/auth/verify-email",
        json={
            "email": user.email.address,
            "token": "abc",
        }
    )
    assert response.status_code == 200, "Status code should be 200"

