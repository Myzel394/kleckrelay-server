import uuid
from dataclasses import dataclass
from datetime import datetime

__all__ = [
    "CronReportBuilder",
]


@dataclass
class CronReportBuilder:
    version = "1.0"
    started_at: datetime
    finished_at: datetime = None
    id: uuid.UUID = None
    status: str = None
    expired_images: int = None
    non_verified_users: int = None

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
