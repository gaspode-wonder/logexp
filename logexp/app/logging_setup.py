# logexp/app/logging_setup.py
#
# Centralized logging configuration for all logexp.* namespaces.
# Ensures structured JSON logs are attached before any app or tests run.

import logging
from logexp.app.logging import StructuredFormatter


def configure_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredFormatter())

    # Namespaces we want structured logs for
    namespaces = [
        "logexp.app",
        "logexp.ingestion",
        "logexp.analytics",
    ]

    for ns in namespaces:
        logger = logging.getLogger(ns)
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = True  # prevent double logs
