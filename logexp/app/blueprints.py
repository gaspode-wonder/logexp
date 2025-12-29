# logexp/app/blueprints.py
"""
Central blueprint registration for LogExp.

This module replaces the legacy app_blueprints.py file and provides
a clean, explicit, modern blueprint registration mechanism.
"""

def register_blueprints(app):
    """
    Register all application blueprints in a single, explicit location.
    Import order is alphabetical for maintainability.
    """

    from .bp.about import bp_about
    from .bp.analytics import bp_analytics
    from .bp.api import bp_api
    from .bp.diagnostics import bp_diagnostics
    from .bp.docs import bp_docs
    from .bp.health import bp_health
    from .bp.settings import bp_settings
    from .bp.ui import bp_ui

    app.register_blueprint(bp_about)
    app.register_blueprint(bp_analytics)
    app.register_blueprint(bp_api)
    app.register_blueprint(bp_diagnostics)
    app.register_blueprint(bp_docs)
    app.register_blueprint(bp_health)
    app.register_blueprint(bp_settings)
    app.register_blueprint(bp_ui)
