from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app import logger
from app.life_constants import MAIL_DOMAIN
from app.models import ReservedAlias, User
from app.models.reserved_alias import ReservedAliasUser as ReservedAliasUserModel
from app.schemas.reserved_alias import (
    ReservedAliasCreate, ReservedAliasCreateUser,
    ReservedAliasUpdate, ReservedAliasUser,
)

__all__ = [
    "find_reserved_aliases_ordered",
    "create_reserved_alias",
    "update_reserved_alias",
    "delete_reserved_alias",
    "get_reserved_alias_by_id",
    "get_reserved_alias_by_address",
]


def _get_users(db: Session, /, users_data: list[ReservedAliasCreateUser]) -> list[User]:
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


def _delete_reverse_alias_users(db: Session, /, alias: ReservedAlias) -> None:
    db.query(ReservedAliasUserModel).filter_by(reserved_alias_id=alias.id).delete()


def find_reserved_aliases_ordered(db: Session, /, search: str = "") -> list[ReservedAlias]:
    logger.info(f"Find reserved aliases ordered -> Finding reserved aliases.")
    query = db.query(ReservedAlias)

    if search:
        logger.info(f"Find reserved aliases ordered -> Filtering by {search=}.")
        query = query.filter(
            func.similarity(ReservedAlias.local, search) > 0.005
        )

    logger.info(f"Find reserved aliases ordered -> Success!.")
    return query\
        .order_by(func.levenshtein(ReservedAlias.local, search) if search else ReservedAlias.local) \
        .all()


def get_reserved_alias_by_id(db: Session, /, alias_id: str) -> ReservedAlias:
    return db.query(ReservedAlias).filter_by(id=alias_id).one()


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
    logger.info(f"Request: Create Reserved Alias -> Creating users {users=}.")
    alias_user = [
        ReservedAliasUserModel(
            user_id=user.id,
            reserved_alias_id=alias.id,
        )
        for user in users
    ]
    logger.info(f"Request: Create Reserved Alias -> Committing users to database.")
    db.add_all(alias_user)
    db.commit()
    db.refresh(alias)

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

    logger.info(f"Request: Update Reserved Alias -> Committing to database.")
    db.add(alias)
    db.commit()
    db.refresh(alias)

    if data.users is not None:
        users = _get_users(db, data.users)
        logger.info(f"Request: Update Reserved Alias -> Changing users.")

        _delete_reverse_alias_users(db, alias)
        alias_user = [
            ReservedAliasUserModel(
                user_id=user.id,
                reserved_alias_id=alias.id,
            )
            for user in users
        ]
        logger.info(f"Request: Create Reserved Alias -> Committing users to database.")
        db.add_all(alias_user)
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


def get_reserved_alias_by_address(
    db: Session,
    /,
    local: str,
    domain: str
) -> Optional[ReservedAlias]:
    logger.info(f"Get reserved alias by address -> Getting alias with {local=} and {domain=}.")
    try:
        alias = db.query(ReservedAlias).filter_by(local=local, domain=domain).one()
    except NoResultFound:
        logger.info(f"Get reserved alias by address -> Alias not found.")
        return None

    logger.info(f"Get reserved alias by address -> Success! Returning alias.")
    return alias
