import uuid
from dataclasses import dataclass
from datetime import datetime

__all__ = [
    "CronReportBuilder",
]


@dataclass
class CronReportBuilder:
    version = "1.0"
    id: uuid.UUID
    started_at: datetime
    finished_at: datetime
    status: str
    expired_images: int
    non_verified_users: int

    def as_dict(self) -> dict[str, str]:
        return {
            "version": self.version,
            "id": str(self.id),
            "report": {
                "started_at": self.started_at.isoformat(),
                "finished_at": self.finished_at.isoformat(),
                "status": self.status,
                "expired_images": self.expired_images,
                "non_verified_users": self.non_verified_users,
            }
        }
