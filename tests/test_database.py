from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.dependencies import get_db
from app.main import app
from app.life_constants import DB_URI

engine = create_engine(DB_URI)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
