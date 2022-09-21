import os
import default_live_constants

__all__ = [
    "DB_URI",
    "MAX_ENCRYPTED_NOTES_SIZE",
    "ACCESS_TOKEN_EXPIRE_IN_MINUTES",
    "REFRESH_TOKEN_EXPIRE_IN_MINUTES",
    "JWT_SECRET_KEY",
    "JWT_REFRESH_SECRET_KEY",
]


DB_URI = os.getenv(
    "DB_URI",
    default=default_live_constants.DB_URI,
)
MAX_ENCRYPTED_NOTES_SIZE = os.getenv(
    "MAX_ENCRYPTED_NOTES_SIZE",
    default=default_live_constants.MAX_ENCRYPTED_NOTES_SIZE,
)
ACCESS_TOKEN_EXPIRE_IN_MINUTES = int(os.getenv(
    "ACCESS_TOKEN_EXPIRE_IN_MINUTES",
    default=default_live_constants.ACCESS_TOKEN_EXPIRE_IN_MINUTES,
))
REFRESH_TOKEN_EXPIRE_IN_MINUTES = int(os.getenv(
    "REFRESH_TOKEN_EXPIRE_IN_MINUTES",
    default=default_live_constants.REFRESH_TOKEN_EXPIRE_IN_MINUTES,
))
JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    default=default_live_constants.JWT_SECRET_KEY,
)
JWT_REFRESH_SECRET_KEY = os.getenv(
    "JWT_REFRESH_SECRET_KEY",
    default=default_live_constants.JWT_REFRESH_SECRET_KEY,
)
