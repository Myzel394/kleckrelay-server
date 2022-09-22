import logging

from app.life_constants import IS_DEBUG

logger = logging.getLogger(__name__)


logger.setLevel(logging.DEBUG)


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

