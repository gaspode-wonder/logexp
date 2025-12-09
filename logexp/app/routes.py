import os
import pytz
from flask import Blueprint, jsonify, request, render_template, current_app
from logexp.app import db
from logexp.app.models import LogExpReading
from logexp.app.schemas import ReadingCreate, ReadingResponse
from logexp.app.geiger import read_geiger
from logexp.app.geiger import list_serial_ports, try_port
from typing import Any

bp = Blueprint("main", __name__)

@bp.get("/")
def index() -> str:
    return render_template("index.html")

@bp.get("/readings")
def get_readings() -> Any:
    readings = LogExpReading.query.order_by(LogExpReading.timestamp.asc()).all()
    responses = [ReadingResponse(**r.to_dict()).dict() for r in readings]
    return jsonify(responses)

@bp.post("/readings")
def create_reading() -> Any:
    payload = request.get_json(force=True, silent=True) or {}
    try:
        validated = ReadingCreate(**payload)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@bp.get("/geiger")
def geiger_live():
    try:
        data = read_geiger("/dev/tty.usbserial-AB9R9IYS")  # adjust port
        return jsonify({"raw": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.get("/geiger/test")
def geiger_test():
    """Report available serial ports and test configured GEIGER_PORT."""
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


@bp.get("/settings")
def settings():
    """Render settings page with available ports."""
    ports = list_serial_ports()
    configured_port = current_app.config["GEIGER_PORT"]
    baudrate = current_app.config["GEIGER_BAUDRATE"]
    return render_template("settings.html", ports=ports, configured_port=configured_port, baudrate=baudrate)

@bp.post("/settings")
def update_settings():
    """Update selected port and baudrate."""
    selected_port = request.form.get("port")
    selected_baudrate = request.form.get("baudrate", "9600")

    # Update config dynamically
    current_app.config["GEIGER_PORT"] = selected_port
    current_app.config["GEIGER_BAUDRATE"] = int(selected_baudrate)

    return redirect(url_for("readings.settings"))

@bp.route("/poller/status")
def poller_status():
    from .poller import poller_instance
    status = "running" if poller_instance and poller_instance.is_alive() else "stopped"
    return jsonify({"poller_status": status})


    reading = LogExpReading(
        counts_per_second=validated.counts_per_second,
        counts_per_minute=validated.counts_per_minute,
        microsieverts_per_hour=validated.microsieverts_per_hour,
        mode=validated.mode,
    )
    db.session.add(reading)
    db.session.commit()

    response = ReadingResponse(**reading.to_dict())
    return jsonify(response.dict()), 201
