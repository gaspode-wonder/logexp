# filename: logexp/app/blueprints.py
"""
Central blueprint registration for LogExp.

This module replaces the legacy app_blueprints.py file and provides
a clean, explicit, modern blueprint registration mechanism.
"""

from __future__ import annotations

from flask import Flask


def register_blueprints(app: Flask) -> None:
    """
    Register all application blueprints in a deterministic order.

    Imports are intentionally local to avoid circular dependencies.
    """
    from .bp.about import bp_about
    from .bp.analytics import bp_analytics
    from .bp.api import bp_api
    from .bp.diagnostics import bp_diagnostics
    from .bp.docs import bp_docs
    from .bp.settings import bp_settings
    from .bp.ui import bp_ui

    app.register_blueprint(bp_ui)
    app.register_blueprint(bp_api)
    app.register_blueprint(bp_settings)
    app.register_blueprint(bp_diagnostics)
    app.register_blueprint(bp_analytics)
    app.register_blueprint(bp_docs)
    app.register_blueprint(bp_about)
