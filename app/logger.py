import logging
import sys

from app.life_constants import IS_DEBUG

logger = logging.getLogger(__name__)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

if IS_DEBUG:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.setLevel(logging.INFO)


def info(msg: str) -> None:
    if IS_DEBUG:
        logger.info(msg)
