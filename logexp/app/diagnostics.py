from flask import Blueprint, render_template, jsonify, current_app

bp = Blueprint("diagnostics", __name__)

@bp.route("/diagnostics")
def diagnostics_index():
    poller = getattr(current_app, "poller", None)
    poller_status = "running" if poller and poller._thread.is_alive() else "stopped"
    return render_template("diagnostics.html", poller_status=poller_status)

@bp.route("/geiger/test")
def diagnostics_test():
    return jsonify({"status": "ok"})
