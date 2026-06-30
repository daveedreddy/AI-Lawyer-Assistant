import logging
from contextlib import contextmanager
from typing import Iterator


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


@contextmanager
def log_operation(operation_name: str) -> Iterator[None]:
    logger = logging.getLogger("ai_lawyer")
    logger.info("Starting %s", operation_name)
    try:
        yield
        logger.info("Completed %s", operation_name)
    except Exception as exc:
        logger.exception("Failed %s: %s", operation_name, exc)
        raise
