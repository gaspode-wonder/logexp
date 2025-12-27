"""
Central blueprint registration for LogExp.

This module replaces the legacy app_blueprints.py file and provides
a clean, explicit, modern blueprint registration mechanism.
"""

def register_blueprints(app):
    from .blueprints.analytics import bp_analytics
    from .blueprints.api import bp_api
    from .blueprints.settings import bp_settings
    from .blueprints.diagnostics import bp_diagnostics
    from .blueprints.docs import bp_docs
    from .blueprints.about import bp_about

    app.register_blueprint(bp_analytics)
    app.register_blueprint(bp_api)
    app.register_blueprint(bp_settings)
    app.register_blueprint(bp_diagnostics)
    app.register_blueprint(bp_docs)
    app.register_blueprint(bp_about)
