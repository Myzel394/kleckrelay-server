from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.life_constants import DB_URI

__all__ = [
    "engine",
    "SessionLocal",
    "Base"
]


engine = create_engine(
    DB_URI,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
