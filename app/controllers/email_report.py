import json

from sqlalchemy.orm import Session

from app.email_report_data import EmailReportData
from app.models import EmailReport, User

__all__ = [
    "create_email_report_from_report_data",
    "get_report_by_id"
]


def create_email_report_from_report_data(
    db: Session,
    /,
    report_data: EmailReportData,
    user: User
) -> EmailReport:
    report = EmailReport(
        user_id=user.id,
        encrypted_content=user.encrypt(json.dumps(report_data.as_dict()))
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


def get_report_by_id(db: Session, id: str) -> EmailReport:
    return db.query(EmailReport).filter_by(id=id).one()
