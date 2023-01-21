from app.life_constants import IS_DEBUG
from app.logger import logger
from app.models import LanguageType
from email_utils.send_mail import send_template_mail

from app import life_constants


def send_email_verification(address: str, token: str, language: LanguageType) -> None:
    logger.info(f"Send Email Verification: Send to {address}.")

    if IS_DEBUG:
        logger.info(f"Send Email Verification: Token for {address} is {token}.")

    verification_url = f"https://{life_constants.APP_DOMAIN}/auth/verify-email?email={address}&token" \
                       f"={token}"

    send_template_mail(
        template="signup",
        to=address,
        subject="Sign up to KleckRelay",
        language=language,
        context={
            "verification_url": verification_url
        }
    )
