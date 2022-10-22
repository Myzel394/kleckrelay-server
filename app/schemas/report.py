from uuid import UUID

from pydantic import BaseModel

__all__ = [
    "Report"
]


class ReportBase(BaseModel):
    pass


class Report(ReportBase):
    id: UUID
    encrypted_content: str

    class Config:
        orm_mode = True
