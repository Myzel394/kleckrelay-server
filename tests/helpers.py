import re

from sqlalchemy.orm import Session


def create_item(db: Session, item: dict, klaas):
    db_item = klaas(**item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def is_a_jwt_token(token: str) -> bool:
    return re.match(r"^(?:[\w-]*\.){2}[\w-]*$", token) is not None
