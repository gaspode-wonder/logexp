# logexp/app/app_blueprints.py
from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for
from logexp.app import db
from logexp.app.models import LogExpReading
from logexp.app.schemas import ReadingCreate, ReadingResponse
from logexp.app.geiger import read_geiger, list_serial_ports, try_port

# ---------------- UI BLUEPRINT ----------------
bp_ui = Blueprint("routes_ui", __name__)

@bp_ui.route("/")
def routes_index():
    # Home now shows readings
    return redirect(url_for("routes_ui.readings_index"))

@bp_ui.route("/readings")
def readings_index():
    readings = LogExpReading.query.order_by(LogExpReading.timestamp.desc()).limit(50).all()
    poller = current_app.poller
    poller_status = "running" if poller and poller._thread.is_alive() else "stopped"
    local_timezone = current_app.config["LOCAL_TIMEZONE"]
    return render_template(
        "readings.html",
        readings=readings,
        poller_status=poller_status,
        local_timezone=local_timezone
    )

@bp_ui.get("/settings")
def settings():
    ports = list_serial_ports()
    configured_port = current_app.config["GEIGER_PORT"]
    baudrate = current_app.config["GEIGER_BAUDRATE"]
    return render_template("settings.html", ports=ports, configured_port=configured_port, baudrate=baudrate)

@bp_ui.post("/settings")
def update_settings():
    selected_port = request.form.get("port")
    selected_baudrate = request.form.get("baudrate", "9600")
    current_app.config["GEIGER_PORT"] = selected_port
    current_app.config["GEIGER_BAUDRATE"] = int(selected_baudrate)
    return redirect(url_for("routes_ui.settings"))

# ---------------- API BLUEPRINT ----------------
bp_api = Blueprint("routes_api", __name__, url_prefix="/api")

@bp_api.get("/readings")
def get_readings():
    readings = LogExpReading.query.order_by(LogExpReading.timestamp.asc()).all()
    responses = [ReadingResponse(**r.to_dict()).model_dump() for r in readings]
    return jsonify(responses)

@bp_api.post("/readings")
def create_reading():
    payload = request.get_json(force=True, silent=True) or {}
    try:
        validated = ReadingCreate(**payload)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    reading = LogExpReading(
        counts_per_second=validated.counts_per_second,
        counts_per_minute=validated.counts_per_minute,
        microsieverts_per_hour=validated.microsieverts_per_hour,
        mode=validated.mode,
    )
    db.session.add(reading)
    db.session.commit()

    response = ReadingResponse(**reading.to_dict())
    return jsonify(response.model_dump()), 201

@bp_api.get("/readings.json")
def readings_json():
    readings = LogExpReading.query.order_by(LogExpReading.timestamp.desc()).limit(50).all()
    return jsonify([r.to_dict() for r in readings])

@bp_api.get("/geiger")
def geiger_live():
    try:
        data = read_geiger(current_app.config["GEIGER_PORT"])
        return jsonify({"raw": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp_api.get("/geiger/test")
def geiger_test():
    results = {}
    ports = list_serial_ports()
    baudrate = current_app.config["GEIGER_BAUDRATE"]
    configured_port = current_app.config["GEIGER_PORT"]

    for port in ports:
        results[port] = try_port(port, baudrate)

    results["configured_port"] = {
        "port": configured_port,
        "test": try_port(configured_port, baudrate)
    }

    if not ports:
        return jsonify({"error": "No serial ports detected"}), 404

    return jsonify(results)

@bp_api.route("/poller/status")
def poller_status():
    poller = current_app.poller
    status = "running" if poller and poller._thread.is_alive() else "stopped"
    return jsonify({"status": status})

@bp_api.route("/poller/start", methods=["POST"])
def poller_start():
    poller = current_app.poller
    if poller and not poller._thread.is_alive():
        poller.start()
        return jsonify({"status": "started"})
    return jsonify({"status": "already running"})

@bp_api.route("/poller/stop", methods=["POST"])
def poller_stop():
    poller = current_app.poller
    if poller and poller._thread.is_alive():
        poller.stop()
        return jsonify({"status": "stopped"})
    return jsonify({"status": "not running"})

@bp_api.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

# ---------------- INFO BLUEPRINT (Docs + About) ----------------
bp_info = Blueprint("info", __name__, url_prefix="/info")

@bp_info.route("/")
def info_index():
    return render_template("info/index.html")

@bp_info.route("/docs")
def info_docs():
    return render_template("info/docs.html")

@bp_info.route("/about")
def info_about():
    return render_template("info/about.html")

# --- Diagnostics Blueprint ---
bp_diagnostics = Blueprint("diagnostics", __name__, url_prefix="/diagnostics")

@bp_diagnostics.route("/")
def diagnostics_index():
    poller = getattr(current_app, "poller", None)
    poller_status = "running" if poller and poller._thread.is_alive() else "stopped"
    return render_template("diagnostics.html", poller_status=poller_status)

@bp_diagnostics.route("/geiger/test")
def diagnostics_test():
    return jsonify({"status": "ok"})

# ---------------- REGISTER ALL ----------------
def register_blueprints(app):
    app.register_blueprint(bp_ui)
    app.register_blueprint(bp_api)
    app.register_blueprint(bp_info)        # combined docs + about
    app.register_blueprint(bp_diagnostics)
