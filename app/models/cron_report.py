from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.models import CreationMixin, IDMixin

__all__ = [
    "CronReportData",
    "CronReport"
]


# This class contains the actual data of the report
class CronReportData(Base, IDMixin):
    __tablename__ = "cron_report_data"

    if TYPE_CHECKING:
        from .user import User
        encrypted_report: str
        user_id: str
        user: User
        report: "CronReport"
        report_id: str
    else:
        encrypted_report = sa.Column(
            sa.String(5_000),
            nullable=False,
        )
        user_id = sa.Column(
            UUID(as_uuid=True),
            sa.ForeignKey("user.id"),
        )
        report_id = sa.Column(
            UUID(as_uuid=True),
            sa.ForeignKey("cron_report.id"),
        )


# This class contains the metadata of the report and includes multiple CronReportDatas
class CronReport(Base, IDMixin, CreationMixin):
    __tablename__ = "cron_report"

    if TYPE_CHECKING:
        report_data: list[CronReportData]
    else:
        report_data = relationship(
            "CronReportData",
            back_populates="report",
        )

