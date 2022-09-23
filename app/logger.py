import logging
import sys
from contextlib import contextmanager

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


@contextmanager
def info_block(msg: str) -> None:
    logger.info(msg)

    try:
        yield
    except Exception:
        logger.info(f"{msg} --- ERROR")
    else:
        logger.info(f"{msg} --- DONE")

