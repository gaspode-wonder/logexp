# filename: logexp/app/logging_setup.py
#
# Centralized logging configuration for all logexp.* namespaces.
# Ensures structured JSON logs are attached before any app or tests run.

from __future__ import annotations

import logging as pylogging
from typing import List

from .logging import StructuredFormatter

# Dedicated logger for setup events
_setup_logger = pylogging.getLogger("logexp.logging.setup")


def configure_logging() -> None:
    """
    Configure structured logging for all logexp.* namespaces.

    - Installs a single StreamHandler with StructuredFormatter
    - Clears existing handlers to prevent duplicates
    - Applies consistent INFO-level logging across the app
    """
    _setup_logger.debug("logging_setup_start")

    handler: pylogging.Handler = pylogging.StreamHandler()
    handler.setFormatter(StructuredFormatter())

    namespaces: List[str] = [
        "beamfoundry.app",
        "logexp.ingestion",
        "logexp.analytics",
        "logexp.validation",
        "logexp.poller",
        "logexp.diagnostics",
        "logexp.api",
        "logexp.extensions",
        "logexp.models",
        "logexp.schemas",
        "logexp.timestamps",
        "logexp.geiger",
        "logexp.blueprints",
        "logexp.logging",
        "logexp.logging.setup",
        "logexp.readings.deprecated",
    ]

    for ns in namespaces:
        logger: pylogging.Logger = pylogging.getLogger(ns)
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(pylogging.INFO)
        logger.propagate = True

        _setup_logger.debug("logging_namespace_configured", extra={"namespace": ns})

    _setup_logger.debug("logging_setup_complete")


def get_logger(name: str) -> pylogging.Logger:
    """
    Obtain a logger for the given namespace.

    Ensures the logger participates in the structured logging setup.
    """
    return pylogging.getLogger(name)
