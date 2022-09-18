import os
import default_live_constants

__all__ = [
    "DB_URI",
]


DB_URI = os.getenv("DB_URI", default=default_live_constants.DB_URI)
