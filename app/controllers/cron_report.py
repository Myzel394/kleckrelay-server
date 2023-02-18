import json

from sqlalchemy.orm import Session

from email_utils.utils import DataclassJSONEncoder
from .admin import get_admin_users
from app.cron_report_builder import CronReportBuilder
from app.models import CronReport, CronReportData, User
from ..gpg_handler import sign_message

__all__ = [
    "create_cron_report",
    "get_latest_cron_report",
]


def create_cron_report(
    db: Session,
    /,
    report_data: CronReportBuilder,
) -> CronReport:
    admins = get_admin_users(db)

    report = CronReport()
    user_encrypted_reports = []

    db.add(report)
    db.commit()
    db.refresh(report)

    report_data.report_id = report.id

    for user in admins:
        encrypted_content = str(sign_message(
            user.encrypt(
                json.dumps(
                    report_data,
                    cls=DataclassJSONEncoder
                ),
            )
        ))
        report_data = CronReportData(
            encrypted_report=encrypted_content,
            user_id=user.id,
            report_id=report.id,
        )

        user_encrypted_reports.append(report_data)

    db.add_all(user_encrypted_reports)
    db.commit()
    db.refresh(report)

    return report


def get_latest_cron_report(db: Session) -> CronReport:
    return db.query(CronReport).order_by(CronReport.created_at.desc()).first()
