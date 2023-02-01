from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import logger
from app.life_constants import MAIL_DOMAIN
from app.models import ReservedAlias, User
from app.schemas.reserved_alias import ReservedAliasCreate, ReservedAliasUpdate, ReservedAliasUser

__all__ = [
    "create_reserved_alias",
    "update_reserved_alias",
    "delete_reserved_alias",
]


def _get_users(db: Session, /, users_data: list[ReservedAliasUser]) -> list[User]:
    logger.info(f"Get users -> Getting users for {users_data=}.")
    user_ids = [
        user.id
        for user in users_data
    ]
    users = db.query(User).filter(User.id.in_(user_ids))
    logger.info(f"Get users -> Found {users.all()=}.")

    logger.info(f"Get users -> Checking length...")
    if users.count() != len(users_data):
        logger.info("Get users -> Couldn't find all users.")
        raise HTTPException(status_code=400, detail="Couldn't find all users.")

    logger.info(f"Get users -> Checking admin...")
    if not all(user.is_admin for user in users):
        logger.info("Get users -> Not all users are admins.")
        raise HTTPException(status_code=400, detail="All users must be admins.")

    logger.info(f"Get users -> Success! Returning users.")
    return users.all()


def create_reserved_alias(db: Session, /, data: ReservedAliasCreate) -> ReservedAlias:
    logger.info(f"Request: Create Reserved Alias -> Creating reserved alias with {data=}.")
    alias = ReservedAlias(
        local=data.local,
        domain=MAIL_DOMAIN,
        is_active=data.is_active,
    )

    logger.info(f"Request: Create Reserved Alias -> Committing to database.")
    db.add(alias)
    db.commit()
    db.refresh(alias)

    users = _get_users(db, data.users)
    logger.info(f"Request: Create Reserved Alias -> Storing users.")
    alias.users.extend(users)

    logger.info(f"Request: Create Reserved Alias -> Success! Returning alias back.")
    return alias


def update_reserved_alias(
    db: Session,
    /,
    alias_id: str,
    data: ReservedAliasUpdate
) -> ReservedAlias:
    logger.info(f"Request: Update Reserved Alias -> Updating alias with {data=}.")
    alias: ReservedAlias = db.query(ReservedAlias).filter_by(id=alias_id).one()

    if data.is_active is not None:
        logger.info(f"Request: Update Reserved Alias -> Changing is_active.")
        alias.is_active = data.is_active

    if data.users is not None:
        users = _get_users(db, data.users)
        logger.info(f"Request: Update Reserved Alias -> Changing users.")

        alias.users.clear()
        alias.users.extend(users)

    logger.info(f"Request: Update Reserved Alias -> Committing to database.")
    db.add(alias)
    db.commit()
    db.refresh(alias)

    logger.info(f"Request: Update Reserved Alias -> Success!")
    return alias


def delete_reserved_alias(db: Session, /, alias_id: str) -> None:
    logger.info(f"Request: Delete Alias -> Deleting {alias_id=}.")
    alias = db.query(ReservedAlias).filter_by(id=alias_id).one()

    logger.info(f"Request: Delete Alias -> Found alias! Committing to database.")
    db.delete(alias)
    db.commit()

    logger.info(f"Request: Delete Alias -> Success!")
    return alias
