import logging
import sys

from app.life_constants import ALLOW_LOGS

logger = logging.getLogger(__name__)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

if ALLOW_LOGS:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.setLevel(logging.INFO)


def info(msg: str) -> None:
    if ALLOW_LOGS:
        logger.info(msg)


def warning(msg: str) -> None:
    logger.warning(msg)
