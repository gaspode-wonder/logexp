# filename: logexp/app/blueprints.py
"""
Central blueprint registration for LogExp.

This module replaces the legacy app_blueprints.py file and provides
a clean, explicit, modern blueprint registration mechanism.
"""

from __future__ import annotations

from flask import Flask

from logexp.app.logging_setup import get_logger

logger = get_logger("logexp.blueprints")


def register_blueprints(app: Flask) -> None:
    """
    Register all application blueprints in a deterministic order.

    Imports are intentionally local to avoid circular dependencies.
    """
    logger.debug("blueprint_registration_start")

    from .bp.about import bp_about
    from .bp.analytics import bp_analytics
    from .bp.api import bp_api
    from .bp.diagnostics import bp_diagnostics
    from .bp.docs import bp_docs
    from .bp.settings import bp_settings
    from .bp.ui import bp_ui

    for bp, name in [
        (bp_ui, "ui"),
        (bp_api, "api"),
        (bp_settings, "settings"),
        (bp_diagnostics, "diagnostics"),
        (bp_analytics, "analytics"),
        (bp_docs, "docs"),
        (bp_about, "about"),
    ]:
        logger.debug("blueprint_register", extra={"blueprint": name})
        app.register_blueprint(bp)

    logger.debug("blueprint_registration_complete")
