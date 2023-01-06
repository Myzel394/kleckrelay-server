import base64
from math import log

from . import constants, default_life_constants, life_constants, logger
from .controllers.alias import generate_id, generate_suffix
from .gpg_handler import gpg
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


def calculate_email_token_brute_force_amount() -> int:
    amount = len(life_constants.RANDOM_EMAIL_ID_CHARS) ** life_constants.RANDOM_EMAIL_ID_MIN_LENGTH

    return int(amount * life_constants.RANDOM_EMAIL_LENGTH_INCREASE_ON_PERCENTAGE)


def validate_value_is_random_string(name: str) -> None:
    value = life_constants.__dict__.get(name, None)
    default_value = default_life_constants.__dict__.get(name, None)

    if value is None:
        logger.warning(
            f"Doctor: `{name}` has not value set. Please set it manually to a random string.\n"
        )
    elif value == default_value:
        logger.warning(
            f"Doctor: `{name}` has not been changed, it's still set to it's default value. "
            f"Please change it to increase the security of your app."
            f"You can do this by editing your `docker_compose.yml` file. Add the following entry "
            f"in the `env` section:\n\n"
            f"{name}=<some random string here, just type randomly on your keyboard>\n\n"
            f"You can also use an online generator for this."
        )
    elif len(value) < 20:
        logger.warning(
            f"Doctor: Your `{name}` is pretty short. We recommend it to have a length of at least "
            "20 characters."
        )


def create_image_proxy_storage_path():
    path = constants.ROOT_DIR / life_constants.IMAGE_PROXY_STORAGE_PATH

    logger.logger.info(
        f"Doctor: Proxied images will be stored in {path}"
    )

    path.mkdir(parents=True, exist_ok=True)


def check_server_private_key():
    key_data = base64.b64decode(life_constants.SERVER_PRIVATE_KEY)

    key = gpg.import_keys(key_data)

    if len(key.fingerprints) == 0:
        logger.warning(
            f"Doctor: Your `SERVER_PRIVATE_KEY` is not a valid GPG key. We strongly recommend "
            f"that you create one for more safety and privacy of your users."
        )


def check_life_constants() -> None:
    validate_value_is_random_string("JWT_SECRET_KEY")
    validate_value_is_random_string("JWT_REFRESH_SECRET_KEY")
    validate_value_is_random_string("SLOW_HASH_SALT")
    validate_value_is_random_string("FAST_HASH_SALT")
    validate_value_is_random_string("USER_PASSWORD_HASH_SALT")

    email_token_entropy = calculate_entropy(
        len(life_constants.EMAIL_LOGIN_TOKEN_CHARS),
        life_constants.EMAIL_LOGIN_TOKEN_LENGTH,
    )

    _get_words()

    logger.logger.info(
        f"Doctor: The entropy of Email-Token-based authentication is about "
        f"{email_token_entropy:.1f}."
    )
    logger.logger.info(
        f"Doctor: The probability of brute-forcing an Email-Login-Token is about "
        f"{format(calculate_email_token_probability() * 100, '.3f')}%."
    )
    logger.logger.info(
        f"Doctor: The domain for the app is: {life_constants.API_DOMAIN}."
    )
    logger.logger.info(
        f"Doctor: The domain for the mails is: {life_constants.MAIL_DOMAIN}."
    )
    logger.logger.info(
        f"Doctor: Random emails will look like this: {generate_id()}@{life_constants.MAIL_DOMAIN}."
    )
    logger.logger.info(
        f"Doctor: Random emails will increase their length after "
        f"{format(calculate_email_token_brute_force_amount(), ',')} generated emails from "
        f"{life_constants.RANDOM_EMAIL_ID_MIN_LENGTH} characters to "
        f"{life_constants.RANDOM_EMAIL_ID_MIN_LENGTH + 1} characters. The percentage value is "
        f"{format(life_constants.RANDOM_EMAIL_LENGTH_INCREASE_ON_PERCENTAGE * 100, '.0f')}%."
    )
    logger.logger.info(
        f"Doctor: Custom emails will look like this: "
        f"awesome-fish.{generate_suffix()}@{life_constants.MAIL_DOMAIN}."
    )

    logger.logger.info(
        f"Doctor: Root dir is: {constants.ROOT_DIR}"
    )

    logger.logger.info(
        f"Doctor: DB URI is: {life_constants.DB_URI.split('@')[1]}"
    )

    if life_constants.USER_EMAIL_ENABLE_DISPOSABLE_EMAILS:
        logger.logger.info(
            "Doctor: Users are allowed to register with disposable emails."
        )
    else:
        logger.logger.info(
            "Doctor: Users are NOT allowed to register with disposable email."
        )

    if life_constants.USER_EMAIL_ENABLE_OTHER_RELAYS:
        logger.logger.info(
            "Doctor: Users are allowed to register with other email relay services."
        )
    else:
        logger.logger.info(
            "Doctor: Users are NOT allowed to register with other email relay services. The "
            f"following domains are not allowed to be used to sign up: {life_constants.USER_EMAIL_OTHER_RELAY_DOMAINS}"
        )

    create_image_proxy_storage_path()

    check_server_private_key()

    if life_constants.INSTANCE_SALT == default_life_constants.INSTANCE_SALT:
        logger.logger.info(
            "Doctor: `INSTANCE_SALT` has not been changed. "
            "Please change it to a random value for increased security "
            "(You can smash any keys on your keyboard. Make sure you use many random characters "
            "and it should be at least 20 characters long)."
        )

    if life_constants.IS_DEBUG:
        logger.logger.warning(
            f"Doctor: <=== DEBUG MODE IS ENABLED, REMEMBER TO DISABLE IT IN PRODUCTION!!! ===>"
        )
