import datetime
import time
from email.utils import format_datetime

__all__ = [
    "format_from_mail",
    "format_date",
]


def format_from_mail(name: str, mail: str) -> str:
    return f'"{name}" <{mail}>'


def format_date() -> str:
    now = time.time()
    date = datetime.datetime.utcfromtimestamp(now)

    return format_datetime(date, False)
