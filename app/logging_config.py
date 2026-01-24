# filename: logexp/app/logging_config.py

import logging as pylogging

from .logging_setup import get_logger

logger = get_logger("beamfoundry.logging.config_legacy")


def configure_logging() -> None:
    """
    Configure application-wide logging for LogExp.
    This function must be import-safe and called only from create_app().
    """
    logger.debug("legacy_logging_setup_start")

    root = pylogging.getLogger()
    root.setLevel(pylogging.INFO)

    handler = pylogging.StreamHandler()
    handler.setLevel(pylogging.INFO)

    formatter = pylogging.Formatter(fmt="level=%(levelname)s subsystem=%(name)s msg=%(message)s")
    handler.setFormatter(formatter)

    root.handlers.clear()
    root.addHandler(handler)

    logger.debug("legacy_logging_handler_installed")

    pylogging.getLogger("logexp").setLevel(pylogging.INFO)

    logger.debug("legacy_logging_namespace_defaults_applied")
    logger.debug("legacy_logging_setup_complete")
