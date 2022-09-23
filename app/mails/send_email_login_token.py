from app.life_constants import IS_DEBUG
from app.logger import logger
from app.models.user import User


def send_email_login_token(user: User, token: str) -> None:
    logger.info(f"Send email login token: Send email to {user.email.address}")

    if IS_DEBUG:
        logger.info(f"Send email login token: Token for {user.email.address} is {token}")
