from app.life_constants import IS_DEBUG
from app.logger import logger


def send_email_verification(address: str, token: str) -> None:
    logger.info(f"Send Email Verification: Send to {address}.")

    if IS_DEBUG:
        logger.info(f"Send Email Verification: Token for {address} is {token}.")
