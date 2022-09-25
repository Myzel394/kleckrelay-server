from math import log

from . import life_constants, logger
from .controllers.alias import generate_id, generate_suffix
from .utils import _get_words

__all__ = [
    "check_life_constants",
]


def calculate_entropy(possibilities: int, length: int) -> float:
    return log(
        possibilities ** length,
        2,
    )


def calculate_email_token_probability() -> float:
    possibilities = len(life_constants.EMAIL_LOGIN_TOKEN_CHARS)

    return sum(
        1 / ((possibilities ** life_constants.EMAIL_LOGIN_TOKEN_LENGTH) - try_count)
        for try_count in range(life_constants.EMAIL_LOGIN_TOKEN_MAX_TRIES)
    )


def check_life_constants() -> None:
    if len(life_constants.JWT_SECRET_KEY) < 20:
        logger.warning(
            "Doctor: We recommend generating a `JWT_SECRET_KEY` of at least 20 characters."
        )

    if len(life_constants.JWT_REFRESH_SECRET_KEY) < 20:
        logger.warning(
            "Doctor: We recommend generating a `JWT_REFRESH_SECRET_KEY` of at least 20 characters."
        )

    email_token_entropy = calculate_entropy(
        len(life_constants.EMAIL_LOGIN_TOKEN_CHARS),
        life_constants.EMAIL_LOGIN_TOKEN_LENGTH,
    )

    logger.logger.info("Caching dictionary")
    _get_words()
    logger.logger.info("Caching dictionary --- DONE!")

    logger.logger.info(
        f"Doctor: Entropy of Email-Token-based authentication is about "
        f"{email_token_entropy:0f}."
    )
    logger.logger.info(
        f"Doctor: The probability of brute-forcing an Email-Login-Token is about "
        f"{format(calculate_email_token_probability() * 100, '.3f')}%."
    )
    logger.logger.info(
        f"Doctor: The domain for the app is: {life_constants.DOMAIN}."
    )
    logger.logger.info(
        f"Doctor: The domain for the mails are: {life_constants.MAIL_DOMAIN}."
    )
    logger.logger.info(
        f"Doctor: Random emails will look like this: {generate_id()}@{life_constants.MAIL_DOMAIN}."
    )
    logger.logger.info(
        f"Doctor: Custom emails will look like this: "
        f"awesome-fish.{generate_suffix()}@{life_constants.MAIL_DOMAIN}."
    )
