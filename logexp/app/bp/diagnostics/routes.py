from flask import render_template, jsonify, current_app
from . import bp_diagnostics

@bp_diagnostics.route("/")
def diagnostics_index():
    poller = getattr(current_app, "poller", None)
    poller_status = "running" if poller and poller._thread.is_alive() else "stopped"
    return render_template("diagnostics.html", poller_status=poller_status)

@bp_diagnostics.get("/")
def diagnostics_index():
    config = current_app.config_obj
    return render_template("diagnostics.html", config=config)

@bp_diagnostics.route("")
def diagnostics_index_no_slash():
    return diagnostics_index()

@bp_diagnostics.route("/geiger/test")
def diagnostics_test():
    return jsonify({"status": "ok"})
