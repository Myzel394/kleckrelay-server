import uuid
from datetime import datetime

from pydantic import BaseModel, Field

__all__ = [
    "CronReportResponseModel",
]

from app.models import CronReport


class CronReportDataResponseModel(BaseModel):
    encrypted_report: str

    class Config:
        orm_mode = True


class CronReportResponseModel(BaseModel):
    id: uuid.UUID
    created_at: datetime
    report_data: CronReportDataResponseModel = Field()  # Select correct "CronReportData" here

    @classmethod
    def from_orm(cls, obj: CronReport, user_id: str):
        response_model = super().from_orm(obj)

        # Select correct "CronReportData" here
        response_model.report_data = CronReportDataResponseModel.from_orm(
            next(
                report
                for report in obj.report_data
                if report.user_id == user_id
            )
        )

        return response_model

    class Config:
        orm_mode = True
