# filename: logexp/app/logging_config.py

import logging

from logexp.app.logging_setup import get_logger

logger = get_logger("logexp.logging.config_legacy")


def configure_logging() -> None:
    """
    Configure application-wide logging for LogExp.
    This function must be import-safe and called only from create_app().
    """
    logger.debug("legacy_logging_setup_start")

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(fmt="level=%(levelname)s subsystem=%(name)s msg=%(message)s")
    handler.setFormatter(formatter)

    root.handlers.clear()
    root.addHandler(handler)

    logger.debug("legacy_logging_handler_installed")

    logging.getLogger("logexp").setLevel(logging.INFO)

    logger.debug("legacy_logging_namespace_defaults_applied")
    logger.debug("legacy_logging_setup_complete")
