from sqlalchemy.orm import Session

from app import logger
from app.life_constants import MAIL_DOMAIN
from app.models import ReservedAlias
from app.schemas.reserved_alias import ReservedAliasCreate, ReservedAliasUpdate

__all__ = [
    "create_reserved_alias",
    "update_reserved_alias",
    "delete_reserved_alias",
]


def create_reserved_alias(db: Session, /, data: ReservedAliasCreate) -> ReservedAlias:
    logger.info(f"Request: Create Reserved Alias -> Creating reserved alias with {data=}.")
    alias = ReservedAlias.create(
        local=data.local,
        domain=MAIL_DOMAIN,
        is_active=data.is_active,
    )

    logger.info(f"Request: Create Reserved Alias -> Committing to database.")
    db.add(alias)
    db.commit()
    db.refresh(alias)

    logger.info(f"Request: Create Reserved Alias -> Storing users.")
    alias.users.add_all(data.users)

    logger.info(f"Request: Create Reserved Alias -> Success! Returning alias back.")
    return alias


def update_reserved_alias(
    db: Session,
    /,
    alias_id: str,
    data: ReservedAliasUpdate
) -> ReservedAlias:
    alias = db.query(ReservedAlias).filter_by(id=alias_id).one()

    if data.is_active is not None:
        alias.is_active = data.is_active

    if data.users is not None:
        alias.users.clear()
        alias.users.add_all(data.users)

    db.add(alias)
    db.commit()
    db.refresh(alias)

    return alias


def delete_reserved_alias(db: Session, /, alias_id: str) -> None:
    alias = db.query(ReservedAlias).filter_by(id=alias_id).one()

    db.delete(alias)
    db.commit()

    return alias
