from app import life_constants
from app.life_constants import IS_DEBUG
from app.logger import logger
from app.models.user import User
from email_utils.send_mail import send_template_mail


def send_email_login_token(user: User, token: str) -> None:
    logger.info(f"Send email login token: Send email to {user.email.address}")

    send_template_mail(
        template="login",
        to=user.email.address,
        subject="Log in to KleckRelay",
        language=user.language,
        context={
            "title": "Log in to KleckRelay",
            "preview_text": "Here's your login code for KleckRelay",
            "body": "Here's your login code for KleckRelay:",
            "code": token,
            "server_url": life_constants.APP_DOMAIN,
        }
    )
