from sqlalchemy.orm import Session

from app.models import ReservedAlias
from app.models.alias import EmailAlias

__all__ = [
    "get_aliases_amount",
    "check_if_alias_exists",
]


def get_aliases_amount(db: Session, /, domain: str) -> int:
    return db.query(EmailAlias).filter_by(domain=domain).count() + \
           db.query(ReservedAlias).filter_by(domain=domain).count()


def check_if_alias_exists(db: Session, /, local: str, domain: str) -> bool:
    return \
        db.query(db
                 .query(EmailAlias)
                 .filter_by(domain=domain)
                 .filter_by(local=local)
                 .exists()
                 ).scalar() or \
        db.query(db
                 .query(ReservedAlias)
                 .filter_by(domain=domain)
                 .filter_by(local=local)
                 .exists()
                 ).scalar()


