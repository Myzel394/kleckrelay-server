import json
from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session

from email_utils.utils import DataclassJSONEncoder
from .admin import get_admin_users
from app.cron_report_builder import CronReportBuilder
from app.models import CronReport, CronReportData
from .. import life_constants
from ..gpg_handler import sign_message

__all__ = [
    "create_cron_report",
    "get_latest_cron_report",
    "get_expired_cron_reports"
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

    report_data.id = report.id

    for user in admins:
        encrypted_content = str(sign_message(
            user.encrypt(
                json.dumps(
                    report_data,
                    cls=DataclassJSONEncoder
                ),
            )
        ))
        data = CronReportData(
            encrypted_report=encrypted_content,
            user_id=user.id,
            report_id=report.id,
        )

        user_encrypted_reports.append(data)

    db.add_all(user_encrypted_reports)
    db.commit()
    db.refresh(report)

    return report


def get_latest_cron_report(db: Session, /) -> CronReport:
    return db.query(CronReport).order_by(CronReport.created_at.desc()).first()


def get_expired_cron_reports(db: Session, /) -> list[CronReport]:
    return db \
        .query(CronReport) \
        .filter(CronReport.created_at < datetime.utcnow() - timedelta(days=life_constants.KEEP_CRON_JOBS_AMOUNT))\
        .all()


def delete_cron_report(db: Session, /, report: CronReport) -> None:
    db.delete(report)
    db.commit()
