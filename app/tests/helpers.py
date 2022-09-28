from sqlalchemy.orm import Session


def create_item(db: Session, item: dict, klaas):
    db_item = klaas(**item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item