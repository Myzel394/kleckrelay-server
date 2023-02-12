import random

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, database_exists
from starlette.testclient import TestClient

from app import constants, life_constants
from app.authentication.handler import access_security, refresh_security
from app.controllers.alias import generate_random_local_id
from app.controllers.email_login import generate_same_request_token, generate_token
from app.database.base import Base
from app.database.dependencies import get_db
from app.life_constants import MAIL_DOMAIN, DB_URI
from app.main import app
from app.models import Email, EmailAlias, EmailLoginToken, ReservedAlias, User, UserPreferences
from app.models.enums.alias import AliasType
from app.tests.helpers import create_item
from app.utils import hash_fast


@pytest.fixture(scope="session", autouse=True)
def update_is_testing():
    constants.IS_TESTING = True


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(DB_URI)
    if not database_exists:
        create_database(engine.url)

    Base.metadata.create_all(bind=engine)

    yield engine


@pytest.fixture(scope="function")
def db(db_engine):
    connection = db_engine.connect()

    # begin a non-ORM transaction
    transaction = connection.begin()

    # bind an individual Session to the connection
    db = Session(bind=connection)
    # db = Session(db_engine)

    constants.TESTING_DB = db

    yield db

    db.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db):
    app.dependency_overrides[get_db] = lambda: db

    with TestClient(app) as c:
        yield c


@pytest.fixture
def create_email(db):
    def _method() -> Email:
        return create_item(
            db,
            {
                "address": f"mail.{random.randint(10000, 99999)}@example.com",
                "is_verified": False,
                "token": "abc",
            },
            Email,
        )

    return _method


@pytest.fixture
def create_user(db, create_email):
    def _method(is_verified=False, is_admin=False, password=None) -> User:
        email = create_email()
        user = create_item(
            db,
            {
                "email": email,
            },
            User,
        )
        email.user_id = user.id

        db.add(email)
        db.commit()

        if is_verified:
            email.is_verified = True

            db.add(email)
            db.commit()

        preferences = create_item(
            db,
            {
                "user_id": user.id,
            },
            UserPreferences,
        )

        db.add(preferences)
        db.commit()

        if is_admin:
            life_constants.ADMINS.append(user.email.address)

        return user

    return _method


@pytest.fixture
def create_email_token(db):
    def _method(user: User) -> tuple[EmailLoginToken, str, str]:
        token = generate_token()
        same_request_token = generate_same_request_token()
        email_login = create_item(
            db,
            {
                "user_id": user.id,
                "token": token,
                "hashed_same_request_token": hash_fast(same_request_token),
            },
            EmailLoginToken
        )

        return email_login, token, same_request_token

    return _method


@pytest.fixture
def create_auth_tokens(db):
    def _method(user: User) -> dict:
        access_token = access_security.create_access_token(subject=user.to_jwt_object()),

        return {
            "access_token": access_token,
            "refresh_token": refresh_security.create_refresh_token(subject=user.to_jwt_object()),
            "headers": {
                "Authorization": f"Bearer {access_token[0]}"
            }
        }

    return _method


@pytest.fixture
def create_random_alias(db):
    def _method(user: User, **kwargs) -> EmailAlias:
        return create_item(
            db,
            {
                "user": user,
                "local": generate_random_local_id(db),
                "domain": MAIL_DOMAIN,
                "type": AliasType.RANDOM,
                **kwargs,
            },
            EmailAlias,
        )

    return _method


@pytest.fixture
def create_reserved_alias(db: Session):
    def _method(users: list[User], **kwargs) -> ReservedAlias:
        alias: ReservedAlias = create_item(
            db,
            {
                "local": generate_random_local_id(db),
                "domain": MAIL_DOMAIN,
                **kwargs,
            },
            ReservedAlias
        )

        alias.users.extend(users)

        return alias

    return _method
