import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models import CronReport

__all__ = [
    "CronReportResponseModel",
]


class CronReportDataResponseModel(BaseModel):
    encrypted_report: str

    class Config:
        orm_mode = True


class CronReportResponseModel(BaseModel):
    id: uuid.UUID
    created_at: datetime
    report_data: CronReportDataResponseModel

    @classmethod
    def from_orm(cls, obj: CronReport, user_id: str):
        response_model = {
            "id": obj.id,
            "created_at":  obj.created_at,
            "report_data": CronReportDataResponseModel.from_orm(
                next(
                    report
                    for report in obj.report_data
                    if report.user_id == user_id
                )
            )}

        # Select correct "CronReportData" here

        return response_model
