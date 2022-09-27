from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from app.database.base import Base
from app.database.dependencies import get_db
from app.main import app

from app import constants

constants.IS_TESTING = True

SQLALCHEMY_DATABASE_URL = "postgresql://user:password@127.0.0.1:35432/mail"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    connection = engine.connect()

    # begin a non-ORM transaction
    transaction = connection.begin()

    # bind an individual Session to the connection
    db = TestingSessionLocal(bind=connection)
    # db = Session(engine)

    yield db

    db.rollback()
    connection.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@app.on_event("startup")
def flush_database():
    print("asdasdsa")
    with TestingSessionLocal() as db:
        db.flush()
