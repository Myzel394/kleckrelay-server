from app import life_constants
from app.helpers.domain import get_top_domain

__all__ = [
    "check_if_email_is_from_relay"
]


def check_if_email_is_from_relay(email: str) -> bool:
    domain = email.split("@")[-1]
    top_domain = get_top_domain(f"https://{domain}")

    return top_domain in life_constants.USER_EMAIL_OTHER_RELAY_DOMAINS
