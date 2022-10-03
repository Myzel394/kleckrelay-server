from contextlib import contextmanager
from typing import ContextManager

from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session

from app import constants
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
    if constants.IS_TESTING:
        yield constants.TESTING_DB

        return

    db = SessionLocal()
    try:
        yield db
    except DatabaseError:
        # Doesn't seem to work
        # db.rollback()
        ...
    finally:
        db.close()
