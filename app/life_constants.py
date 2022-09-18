import os
import default_live_constants

__all__ = [
    "DB_URI",
    "MAX_ENCRYPTED_NOTES_SIZE"
]


DB_URI = os.getenv(
    "DB_URI",
    default=default_live_constants.DB_URI,
)
MAX_ENCRYPTED_NOTES_SIZE = os.getenv(
    "MAX_ENCRYPTED_NOTES_SIZE",
    default=default_live_constants.MAX_ENCRYPTED_NOTES_SIZE,
)
