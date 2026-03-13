"""Structured logging for the code review skill."""

import logging
import time
from contextlib import contextmanager


def get_logger(name: str) -> logging.Logger:
    """Get a logger with a consistent format for the code review skill."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def estimate_tokens(text: str) -> int:
    """Estimate token count using word_count * 1.3 heuristic."""
    word_count = len(text.split())
    return int(word_count * 1.3)


@contextmanager
def log_timing(logger: logging.Logger, operation: str):
    """Context manager that logs the duration of an operation."""
    start = time.perf_counter()
    logger.info("Starting %s", operation)
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info("Completed %s in %.1fms", operation, elapsed_ms)
