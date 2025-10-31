"""Logging configuration for pieces service.

Provides standardized logging setup for API and client operations.
"""

from __future__ import annotations

import logging
import sys


def configure_logging() -> None:
    """Set up logging with standard format and handlers."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def get_logger(name: str) -> logging.Logger:
    """Get configured logger for a module.

    @param name: Logger name (usually __name__).
    @return: Configured logger instance.
    """
    return logging.getLogger(name)
