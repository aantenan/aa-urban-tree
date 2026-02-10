"""Structured logging configuration."""
import logging
import sys
from typing import Any

from config import LOG_LEVEL


def setup_logging() -> None:
    """Configure root logger with structured format for production."""
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
    )
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a logger for the given module name."""
    return logging.getLogger(name)
