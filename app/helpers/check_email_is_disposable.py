import requests

from app import constants

__all__ = [
    "check_if_email_is_disposable",
]


def check_if_email_is_disposable(email: str) -> bool:
    if constants.IS_TESTING:
        return False

    domain = email.split("@")[-1]
    
    response = requests.get(
        f"https://api.mailcheck.ai/domain/{domain}",
    )

    response.raise_for_status()

    data = response.json()

    return not (data["mx"] is True and data["disposable"] is False)
