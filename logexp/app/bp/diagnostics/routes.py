from flask import current_app, jsonify, render_template

from . import bp_diagnostics


# ---------------------------------------------------------------------------
# Diagnostics Home
# ---------------------------------------------------------------------------
@bp_diagnostics.route("/", methods=["GET"])
def diagnostics_index():
    """
    Render the diagnostics page with poller status and config.
    """
    poller = getattr(current_app, "poller", None)
    poller_status = "running" if poller and poller._thread.is_alive() else "stopped"

    # Centralized config object (from load_config)
    config = getattr(current_app, "config_obj", {})

    return render_template(
        "diagnostics.html",
        poller_status=poller_status,
        config=config,
    )


# Support /diagnostics (no trailing slash)
@bp_diagnostics.route("", methods=["GET"])
def diagnostics_index_no_slash():
    return diagnostics_index()


# ---------------------------------------------------------------------------
# Diagnostics JSON test endpoint
# ---------------------------------------------------------------------------
@bp_diagnostics.route("/geiger/test", methods=["GET"])
def diagnostics_test():
    return jsonify({"status": "ok"})
