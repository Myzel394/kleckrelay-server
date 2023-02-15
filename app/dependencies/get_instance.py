import uuid
from typing import Any, Callable, TypeVar

from fastapi import Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app import logger
from app.database.dependencies import get_db
from app.dependencies.get_user import get_user
from app.models import User

__all__ = [
    "get_instance"
]

T = TypeVar("T")


def get_instance(
    getter_func: Callable[[Session, User, uuid.UUID], T]
) -> Callable[[uuid.UUID, Session, User], T]:
    def wrapper(
        instance_id: uuid.UUID,
        db: Session = Depends(get_db),
        user: User = Depends(get_user),
    ):
        try:
            logger.info(
                f"Request: Get Instance -> Getting instance with id={instance_id}. "
                f"Using function {getter_func.__name__}."
            )
            return getter_func(db, user=user, id=instance_id)
        except NoResultFound:
            logger.info(f"Request: Get Instance -> Instance with id={instance_id} not found.")
            raise HTTPException(
                status_code=404,
                detail="Object not found."
            )

    return wrapper
