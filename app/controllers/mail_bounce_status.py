import uuid

from sqlalchemy.orm import Session

from app.models import MailBounceStatus

__all__ = [
    "create_bounce_status",
    "update_bounce_status_to_bounce",
    "get_bounce_status_by_id",
]


def create_bounce_status(
    db: Session,
    /,
    from_address: str,
    to_address: str,
) -> MailBounceStatus:
    status = MailBounceStatus(
        from_address=from_address,
        to_address=to_address,
    )

    db.add(status)
    db.commit()
    db.refresh(status)

    return status


def update_bounce_status_to_bounce(
    db: Session,
    /,
    bounce_status: MailBounceStatus
) -> MailBounceStatus:
    bounce_status.status = "bouncing"

    db.add(bounce_status)
    db.commit()
    db.refresh(bounce_status)

    return bounce_status


def get_bounce_status_by_id(
    db: Session,
    /,
    bounce_status_id: int,
) -> MailBounceStatus:
    return db.query(MailBounceStatus).filter_by(id=bounce_status_id).one()
