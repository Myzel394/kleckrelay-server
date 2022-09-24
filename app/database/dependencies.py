from sqlalchemy.exc import DatabaseError

from app.database.base import SessionLocal

__all__ = [
    "get_db",
]


def get_db():
    db = SessionLocal()
    try:
        yield db
    except DatabaseError:
        # Doesn't seem to work
        # db.rollback()
        ...
    finally:
        db.close()
