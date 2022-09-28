import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, database_exists
from starlette.testclient import TestClient

from app.database.base import Base
from app.database.dependencies import get_db
from app.main import app
from app.models import Email, EmailLoginToken, User
from app.tests.helpers import create_item

SQLALCHEMY_DATABASE_URL = "postgresql://user:password@127.0.0.1:35432/mail"


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
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

    yield db

    db.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db):
    app.dependency_overrides[get_db] = lambda: db

    with TestClient(app) as c:
        yield c


@pytest.fixture
def email(db) -> Email:
    return create_item(
        db,
        {
            "address": "email@example.com",
            "is_verified": False,
            "token": "abc",
        },
        Email,
    )


@pytest.fixture
def create_user(db, email) -> User:
    def _method(is_verified=False):
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

        return user

    return _method


@pytest.fixture
def create_email_token(db) -> EmailLoginToken:
    def _method(user: User):
        token = create_item(
            db,
            {
                "user_id": user.id,
            },
            EmailLoginToken
        )

        return token

    return _method
