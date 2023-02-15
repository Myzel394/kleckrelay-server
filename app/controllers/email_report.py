import json
import uuid

from sqlalchemy.orm import Session

from app.email_report_data import EmailReportData
from app.gpg_handler import sign_message
from app.models import EmailReport, User

from email_utils.utils import DataclassJSONEncoder

__all__ = [
    "create_email_report",
    "get_report_from_user_by_id",
    "delete_report",
]


def create_email_report(
    db: Session,
    /,
    report_data: EmailReportData,
    user: User
) -> EmailReport:
    report = EmailReport(
        user_id=user.id,
        encrypted_content="",
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    report_data.report_id = report.id
    report.encrypted_content = str(sign_message(
        user.encrypt(
            json.dumps(
                report_data,
                cls=DataclassJSONEncoder
            ),
        )
    ))

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


def get_report_from_user_by_id(db: Session, user: User, id: uuid.UUID) -> EmailReport:
    return db.query(EmailReport).filter_by(user_id=user.id, id=id).one()


def delete_report(db: Session, report: EmailReport) -> None:
    db.delete(report)
    db.commit()
