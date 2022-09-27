from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.dependencies import get_db
from app.main import app
from app.tests.conftest import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
