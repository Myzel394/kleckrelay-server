from contextlib import contextmanager
from typing import ContextManager

from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session

from app.database.base import SessionLocal

__all__ = [
    "get_db",
    "with_db",
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


@contextmanager
def with_db() -> ContextManager[Session]:
    db = SessionLocal()
    try:
        yield db
    except DatabaseError:
        # Doesn't seem to work
        # db.rollback()
        ...
    finally:
        db.close()
