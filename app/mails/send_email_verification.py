from collections import namedtuple
from urllib.parse import urlencode, urlunparse

from app.life_constants import IS_DEBUG
from app.logger import logger
from app.models import LanguageType
from email_utils.send_mail import draft_message, send_mail, send_template_mail

from app import life_constants
from email_utils.template_renderer import render

Components = namedtuple(
    typename='Components',
    field_names=['scheme', 'netloc', 'url', 'path', 'query', 'fragment']
)


def _generate_url(email: str, token: str) -> str:
    scheme = "https" if not IS_DEBUG else "http"
    query_parameters = {
        "email": email,
        "token": token,
    }

    return urlunparse(
        Components(
            scheme=scheme,
            netloc=life_constants.APP_DOMAIN,
            url="/auth/verify-email",
            path="",
            query=urlencode(query_parameters),
        )
    )


def send_email_verification(address: str, token: str, language: LanguageType) -> None:
    logger.info(f"Send Email Verification: Send to {address}.")

    verification_url = _generate_url(email=address, token=token)

    send_mail(
        message=draft_message(
            subject="Log in to KleckRelay",
            html=render(
                "signup",
                title="Sign up to KleckRelay",
                preview_text="Confirm your email address to use KleckRelay",
                body="Welcome to KleckRelay! Please click the button below to verify your email address.",
                verify_url=verification_url,
                body_not_requested="If you did not request this email, please ignore it.",
                server_url=life_constants.APP_DOMAIN,
            ),
        ),
        to_mail=address,
    )
