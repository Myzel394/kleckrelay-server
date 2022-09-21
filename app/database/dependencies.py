from app.database.base import SessionLocal

__all__ = [
    "get_db",
]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
