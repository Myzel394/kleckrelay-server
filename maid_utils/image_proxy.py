import shutil
from datetime import date, datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.controllers import global_settings as settings
from email_utils.image_proxy import STORAGE_PATH


__all__ = [
    "delete_expired_images",
]


def delete_expired_images(db: Session, /) -> int:
    life_time_in_hours = settings.get(db, "IMAGE_PROXY_STORAGE_LIFE_TIME_IN_HOURS")
    count = 0

    for result in Path(STORAGE_PATH).iterdir():
        if result.is_dir():
            d = datetime.strptime(result.name, "%Y-%m-%d").date()
            diff = date.today() - d
            diff_in_hours = diff.days * 24

            if diff_in_hours >= life_time_in_hours:
                shutil.rmtree(str(result))
                count += 1

    return count
