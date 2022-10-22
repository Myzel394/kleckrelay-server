import datetime
from dataclasses import dataclass, field
from typing import Optional

_all__ = [
    "EmailReportProxyImageData",
    "EmailReportSinglePixelImageTrackerData",
    "EmailReportData",
]


@dataclass
class EmailReportProxyImageData:
    url: str
    image_proxy_id: str
    server_url: str
    created_at: datetime.datetime

    def as_dict(self) -> dict[str, str]:
        return {
            "url": self.url,
            "image_proxy_id": str(self.image_proxy_id),
            "server_url": self.server_url,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class EmailReportSinglePixelImageTrackerData:
    source: str
    tracker_name: str
    tracker_url: str

    def as_dict(self) -> dict[str, str]:
        return {
            "source": self.source,
            "tracker_name": self.tracker_name,
            "tracker_url": self.tracker_url,
        }


@dataclass
class EmailReportData:
    version = "1.0"
    mail_from: str
    mail_to: str
    subject: str
    message_id: str
    report_id: Optional[str] = None
    proxied_images: list[EmailReportProxyImageData] = field(
        default_factory=lambda: []
    )
    single_pixel_images: list[EmailReportSinglePixelImageTrackerData] = field(
        default_factory=lambda: []
    )

    def as_dict(self) -> dict:
        assert self.report_id is not None, \
            "`report_id` is missing. This value must be set manually."

        return {
            "version": self.version,
            "id": str(self.report_id),
            "message_details": {
                "meta": {
                    "message_id": self.message_id,
                    "from": self.mail_from,
                    "to": self.mail_to,
                    "created_at": datetime.datetime.now().isoformat(),
                },
                "content": {
                    "subject": self.subject,
                    "proxied_images": [
                        image.as_dict()
                        for image in self.proxied_images
                    ],
                    "single_pixel_images": [
                        single_pixel_image.as_dict()
                        for single_pixel_image in self.single_pixel_images
                    ]
                }
            }
        }

