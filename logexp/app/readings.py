from flask import Blueprint, render_template, jsonify, current_app
from logexp.app.models import LogExpReading

# HTML page blueprint
bp_ui = Blueprint("readings_ui", __name__)

@bp_ui.route("/readings")
def readings_index():
    readings = LogExpReading.query.order_by(LogExpReading.timestamp.desc()).limit(50).all()
    poller = current_app.poller
    poller_status = "running" if poller and poller._thread.is_alive() else "stopped"
    return render_template("readings.html", readings=readings, poller_status=poller_status)

# API blueprint
bp_api = Blueprint("readings_api", __name__, url_prefix="/api")

@bp_api.route("/readings.json")
def readings_json():
    readings = LogExpReading.query.order_by(LogExpReading.timestamp.desc()).limit(50).all()
    return jsonify([r.to_dict() for r in readings])
