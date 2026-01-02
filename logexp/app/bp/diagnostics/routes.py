# filename: logexp/app/bp/diagnostics/routes.py

from __future__ import annotations

from datetime import datetime, timezone

from flask import current_app, jsonify, render_template

from logexp.app.bp.diagnostics import bp_diagnostics
from logexp.app.services.analytics_diagnostics import get_analytics_status
from logexp.app.services.database_diagnostics import get_database_status
from logexp.app.services.ingestion import get_ingestion_status
from logexp.app.services.poller import get_poller_status


# ---------------------------------------------------------------------------
# Diagnostics UI (HTML)
# ---------------------------------------------------------------------------
@bp_diagnostics.get("/")
def diagnostics_page():
    """
    Diagnostics UI entrypoint.

    Renders a template with the same shape as /api/diagnostics, so
    the template can trust a stable contract:

        - config
        - ingestion
        - poller
        - analytics
        - database
        - meta
    """
    config = getattr(current_app, "config_obj", {})

    now = datetime.now(timezone.utc)

    context = {
        "config": dict(config),
        "ingestion": get_ingestion_status(),
        "poller": get_poller_status(),
        "analytics": get_analytics_status(),
        "database": get_database_status(),
        "meta": {
            "timestamp": now.isoformat(),
        },
    }

    return render_template("diagnostics.html", **context)


# ---------------------------------------------------------------------------
# Legacy endpoint name used in templates/tests
# ---------------------------------------------------------------------------
@bp_diagnostics.get("/index", endpoint="diagnostics_index")
def diagnostics_index():
    return diagnostics_page()


# ---------------------------------------------------------------------------
# Support /diagnostics (no trailing slash)
# ---------------------------------------------------------------------------
@bp_diagnostics.get("")
def diagnostics_page_no_slash():
    return diagnostics_page()


# ---------------------------------------------------------------------------
# Minimal JSON test endpoint (legacy)
# ---------------------------------------------------------------------------
@bp_diagnostics.get("/geiger/test")
def diagnostics_test():
    """
    Legacy JSON test endpoint.
    Retained for backward compatibility with older test suites.
    """
    return jsonify({"status": "ok"})
