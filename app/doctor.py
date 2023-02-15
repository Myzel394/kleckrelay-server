import base64
from math import log

from . import constants, default_life_constants, life_constants, logger
from .gpg_handler import gpg
from .utils.common import _get_words

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

    if key_data == default_life_constants.SERVER_PRIVATE_KEY:
        logger.warning(
            f"Doctor: Your `SERVER_PRIVATE_KEY` has not been set. We strongly recommend that you "
            f"create one for more safety and privacy of your users."
        )
        return

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

    # Cache word list
    _get_words()

    logger.logger.info(
        f"Doctor: App Domain: {life_constants.API_DOMAIN}."
    )
    logger.logger.info(
        f"Doctor: Mail Domain: {life_constants.MAIL_DOMAIN}."
    )

    create_image_proxy_storage_path()

    check_server_private_key()

    if life_constants.INSTANCE_SALT == default_life_constants.INSTANCE_SALT:
        logger.logger.warning(
            "Doctor: `INSTANCE_SALT` has not been changed. "
            "Please change it to a random value for increased security "
            "(You can smash any keys on your keyboard. Make sure you use many random characters "
            "and it should be at least 20 characters long)."
        )

    if len(life_constants.ADMINS) > 0:
        logger.logger.info(
            f"Doctor: Admins are: {', '.join(life_constants.ADMINS)}"
        )

    if life_constants.IS_DEBUG:
        logger.logger.warning(
            f"Doctor: <=== DEBUG MODE IS ENABLED, REMEMBER TO DISABLE IT IN PRODUCTION!!! ===>"
        )

    logger.logger.info(f"Doctor: Check completed")
