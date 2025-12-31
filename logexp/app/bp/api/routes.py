from flask import current_app, jsonify, request

from logexp.app import db
from logexp.app.geiger import list_serial_ports, read_geiger, try_port
from logexp.app.models import LogExpReading
from logexp.app.schemas import ReadingCreate, ReadingResponse

from . import bp_api


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
    readings = (
        LogExpReading.query.order_by(LogExpReading.timestamp.desc()).limit(50).all()
    )
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
        "test": try_port(configured_port, baudrate),
    }

    if not ports:
        return jsonify({"error": "No serial ports detected"}), 404

    return jsonify(results)


@bp_api.get("/poller/status")
def poller_status():
    poller = getattr(current_app, "poller", None)
    status = "running" if poller and poller._thread.is_alive() else "stopped"
    return jsonify({"status": status})


@bp_api.post("/poller/start")
def poller_start():
    poller = getattr(current_app, "poller", None)
    if poller and not poller._thread.is_alive():
        poller.start()
        return jsonify({"status": "started"})
    return jsonify({"status": "already running"})


@bp_api.post("/poller/stop")
def poller_stop():
    poller = getattr(current_app, "poller", None)
    if poller and poller._thread.is_alive():
        poller.stop()
        return jsonify({"status": "stopped"})
    return jsonify({"status": "not running"})


@bp_api.get("/health")
def health():
    return jsonify({"status": "ok"}), 200
