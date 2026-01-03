# filename: logexp/app/logging_setup.py
#
# Centralized logging configuration for all logexp.* namespaces.
# Ensures structured JSON logs are attached before any app or tests run.

from __future__ import annotations

import logging
from typing import List

from logexp.app.logging import StructuredFormatter


def configure_logging() -> None:
    """
    Configure structured logging for all logexp.* namespaces.

    - Installs a single StreamHandler with StructuredFormatter
    - Clears existing handlers to prevent duplicates
    - Applies consistent INFO-level logging across the app
    """
    handler: logging.Handler = logging.StreamHandler()
    handler.setFormatter(StructuredFormatter())

    namespaces: List[str] = [
        "logexp.app",
        "logexp.ingestion",
        "logexp.analytics",
        "logexp.validation",
    ]

    for ns in namespaces:
        logger: logging.Logger = logging.getLogger(ns)
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = True


def get_logger(name: str) -> logging.Logger:
    """
    Obtain a logger for the given namespace.

    Ensures the logger participates in the structured logging setup.
    """
    return logging.getLogger(name)
