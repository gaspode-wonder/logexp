# logexp/app/app_blueprints.py
from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for
from logexp.app import db
from logexp.app.models import LogExpReading
from logexp.app.schemas import ReadingCreate, ReadingResponse
from logexp.app.geiger import read_geiger, list_serial_ports, try_port
from datetime import datetime, timedelta
import matplotlib
matplotlib.use("Agg")   # must be set before importing pyplot
import matplotlib.pyplot as plt
import os

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

# --- Analytics Blueprint ---
bp_analytics = Blueprint("analytics", __name__, url_prefix="/analytics")
from datetime import datetime, timedelta

@bp_analytics.route("/", methods=["GET"])
def analytics_index():
    # Query params
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    metric = request.args.get("metric", "cpm")
    quick_range = request.args.get("range")

    # Default: last 24h if no params
    if not start_date and not end_date and not quick_range:
        default_start = datetime.now() - timedelta(hours=24)
        start_date = default_start.isoformat(timespec="minutes")
        end_date = datetime.now().isoformat(timespec="minutes")

    # Handle quick range buttons
    if quick_range:
        now = datetime.now()
        if quick_range == "1h":
            start_date = (now - timedelta(hours=1)).isoformat(timespec="minutes")
        elif quick_range == "24h":
            start_date = (now - timedelta(hours=24)).isoformat(timespec="minutes")
        elif quick_range == "7d":
            start_date = (now - timedelta(days=7)).isoformat(timespec="minutes")
        end_date = now.isoformat(timespec="minutes")

    # Build query
    query = LogExpReading.query
    if start_date:
        try:
            query = query.filter(LogExpReading.timestamp >= datetime.fromisoformat(start_date))
        except ValueError:
            current_app.logger.warning(f"Invalid start_date: {start_date}")
    if end_date:
        try:
            query = query.filter(LogExpReading.timestamp <= datetime.fromisoformat(end_date))
        except ValueError:
            current_app.logger.warning(f"Invalid end_date: {end_date}")

    readings = query.order_by(LogExpReading.timestamp).all()

    chart_url = None
    if readings:
        try:
            timestamps = [r.timestamp for r in readings]
            if metric == "cps":
                values = [r.counts_per_second for r in readings]
                ylabel = "Counts per Second (CPS)"
            elif metric == "usvh":
                values = [r.microsieverts_per_hour for r in readings]
                ylabel = "µSv/h"
            else:
                values = [r.counts_per_minute for r in readings]
                ylabel = "Counts per Minute (CPM)"

            plt.figure(figsize=(8,4))
            plt.plot(timestamps, values, marker="o", linestyle="-", color="blue")
            plt.title(f"{ylabel} Over Time")
            plt.xlabel("Timestamp")
            plt.ylabel(ylabel)
            plt.xticks(rotation=45)
            plt.tight_layout()

            static_path = os.path.join(current_app.root_path, "static", "analytics.png")
            plt.savefig(static_path)
            plt.close()

            chart_url = "/static/analytics.png"
        except Exception as e:
            current_app.logger.error(f"Chart generation failed: {e}")

    return render_template(
        "analytics.html",
        readings=readings,
        chart_url=chart_url,
        start_date=start_date,
        end_date=end_date,
        metric=metric
    )

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    metric = request.args.get("metric", "cpm")

    query = LogExpReading.query

    if start_date:
        try:
            query = query.filter(LogExpReading.timestamp >= datetime.fromisoformat(start_date))
        except ValueError:
            current_app.logger.warning(f"Invalid start_date: {start_date}")

    if end_date:
        try:
            query = query.filter(LogExpReading.timestamp <= datetime.fromisoformat(end_date))
        except ValueError:
            current_app.logger.warning(f"Invalid end_date: {end_date}")

    readings = query.order_by(LogExpReading.timestamp).all()
    # chart generation logic unchanged...


    chart_url = None
    if readings:
        try:
            timestamps = [r.timestamp for r in readings]

            if metric == "cps":
                values = [r.counts_per_second for r in readings]
                ylabel = "Counts per Second (CPS)"
            elif metric == "usvh":
                values = [r.microsieverts_per_hour for r in readings]
                ylabel = "µSv/h"
            else:
                values = [r.counts_per_minute for r in readings]
                ylabel = "Counts per Minute (CPM)"

            plt.figure(figsize=(8,4))
            plt.plot(timestamps, values, marker="o", linestyle="-", color="blue")
            plt.title(f"{ylabel} Over Time (Last 24h)")
            plt.xlabel("Timestamp")
            plt.ylabel(ylabel)
            plt.xticks(rotation=45)
            plt.tight_layout()

            static_path = os.path.join(current_app.root_path, "static", "analytics.png")
            plt.savefig(static_path)
            plt.close()

            chart_url = "/static/analytics.png"

        except Exception as e:
            current_app.logger.error(f"Chart generation failed: {e}")
            chart_url = None

    return render_template("analytics.html", readings=readings, chart_url=chart_url)



# ---------------- REGISTER ALL ----------------
def register_blueprints(app):
    app.register_blueprint(bp_ui)
    app.register_blueprint(bp_api)
    app.register_blueprint(bp_info)        # combined docs + about
    app.register_blueprint(bp_diagnostics)
    app.register_blueprint(bp_analytics)
