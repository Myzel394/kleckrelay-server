from app import life_constants
from app.life_constants import IS_DEBUG
from app.logger import logger
from app.models.user import User
from email_utils.send_mail import draft_message, send_mail, send_template_mail
from email_utils.template_renderer import render


def send_email_login_token(user: User, token: str) -> None:
    logger.info(f"Send email login token: Send email to {user.email.address}")

    send_mail(
        message=draft_message(
            subject="Log in to KleckRelay",
            html=render(
                "login",
                title="Log in to KleckRelay",
                preview_text="Here's your login code for KleckRelay",
                body="Here's your login code for KleckRelay:",
                code=token,
                server_url=life_constants.APP_DOMAIN,
            ),
        ),
        to_mail=user.email.address,
    )
