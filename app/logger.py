import logging
import sys

from app.life_constants import IS_DEBUG

logger = logging.getLogger(__name__)

if IS_DEBUG:
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(sys.stdout))


def info(msg: str) -> None:
    if IS_DEBUG:
        logger.info(msg)


def info_block(msg: str) -> None:
    logger.info(msg)

    try:
        yield
    except Exception:
        logger.info(f"{msg} --- ERROR")
    else:
        logger.info(f"{msg} --- DONE")

