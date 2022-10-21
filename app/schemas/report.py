from pydantic import BaseModel

__all__ = [
    "Report"
]


class ReportBase(BaseModel):
    pass


class Report(ReportBase):
    encrypted_content: str
