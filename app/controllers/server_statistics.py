from typing import Optional

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app import life_constants

from app.models import ServerStatistics

__all__ = [
    "get_server_statistics",
    "add_sent_email",
    "add_expanded_urls",
    "add_proxied_images",
    "add_removed_trackers"
]


def get_server_statistics(db: Session, /) -> Optional[ServerStatistics]:
    """Returns a `SeverStatistics`. Ensures only one `ServerStatistics` exists."""
    if not life_constants.ALLOW_STATISTICS:
        return None

    try:
        return db.query(ServerStatistics).one()
    except NoResultFound:
        statistics = ServerStatistics()

        db.add(statistics)
        db.commit()

        return statistics


def add_sent_email(db: Session, /) -> None:
    statistics = get_server_statistics(db)

    if statistics is None:
        return

    statistics.sent_emails_amount += 1

    db.add(statistics)
    db.commit()
    db.refresh(statistics)


def add_proxied_images(db: Session, /, amount: int) -> None:
    statistics = get_server_statistics(db)

    if statistics is None:
        return

    statistics.proxied_images_amount += amount

    db.add(statistics)
    db.commit()
    db.refresh(statistics)


def add_expanded_urls(db: Session, /, amount: int) -> None:
    statistics = get_server_statistics(db)

    if statistics is None:
        return

    statistics.expanded_urls_amount += amount

    db.add(statistics)
    db.commit()
    db.refresh(statistics)


def add_removed_trackers(db: Session, /, amount: int) -> None:
    statistics = get_server_statistics(db)

    if statistics is None:
        return

    statistics.trackers_removed_amount += amount

    db.add(statistics)
    db.commit()
    db.refresh(statistics)