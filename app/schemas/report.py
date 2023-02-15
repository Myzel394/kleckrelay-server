import uuid

from pydantic import BaseModel

__all__ = [
    "Report"
]


class ReportBase(BaseModel):
    pass


class Report(ReportBase):
    id: uuid.UUID
    encrypted_content: str

    class Config:
        orm_mode = True
