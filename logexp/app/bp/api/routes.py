# logexp/app/bp/api/routes.py

from typing import Any

from flask import current_app, jsonify, request

from logexp.app import db
from logexp.app.bp.api import bp_api
from logexp.app.geiger import list_serial_ports, read_geiger, try_port
from logexp.app.models import LogExpReading
from logexp.app.schemas import ReadingCreate, ReadingResponse


@bp_api.get("/readings")
def get_readings() -> Any:
    readings = LogExpReading.query.order_by(LogExpReading.timestamp.asc()).all()
    responses = [ReadingResponse(**r.to_dict()).model_dump() for r in readings]
    return jsonify(responses)


@bp_api.post("/readings")
def create_reading() -> Any:
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
def readings_json() -> Any:
    readings = (
        LogExpReading.query.order_by(LogExpReading.timestamp.desc()).limit(50).all()
    )
    return jsonify([r.to_dict() for r in readings])


@bp_api.get("/geiger")
def geiger_live() -> Any:
    try:
        data = read_geiger(
            current_app.config["GEIGER_PORT"],
            current_app.config["GEIGER_BAUDRATE"],
        )
        return jsonify({"raw": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp_api.get("/geiger/test")
def geiger_test() -> Any:
    results: dict[str, Any] = {}
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
def poller_status() -> Any:
    poller = getattr(current_app, "poller", None)
    status = "running" if poller and poller._thread.is_alive() else "stopped"
    return jsonify({"status": status})


@bp_api.post("/poller/start")
def poller_start() -> Any:
    poller = getattr(current_app, "poller", None)
    if poller and not poller._thread.is_alive():
        poller.start()
        return jsonify({"status": "started"})
    return jsonify({"status": "already running"})


@bp_api.post("/poller/stop")
def poller_stop() -> Any:
    poller = getattr(current_app, "poller", None)
    if poller and poller._thread.is_alive():
        poller.stop()
        return jsonify({"status": "stopped"})
    return jsonify({"status": "not running"})


@bp_api.get("/health")
def health() -> Any:
    return jsonify({"status": "ok"}), 200


@bp_api.get("/diagnostics")
def diagnostics_api() -> Any:
    """
    Unified diagnostics API endpoint.

    Aggregates config, ingestion, poller, analytics, and database diagnostics
    into a single JSON payload suitable for the UI and CI smoke tests.
    """
    from datetime import datetime, timezone
    from typing import Any

    from logexp.app.services.analytics_diagnostics import get_analytics_status
    from logexp.app.services.database_diagnostics import get_database_status
    from logexp.app.services.ingestion import get_ingestion_status
    from logexp.app.services.poller import get_poller_status

    config = getattr(current_app, "config_obj", {})

    now = datetime.now(timezone.utc)

    payload = {
        "config": dict(config),
        "ingestion": get_ingestion_status(),
        "poller": get_poller_status(),
        "analytics": get_analytics_status(),
        "database": get_database_status(),
        "meta": {
            "timestamp": now.isoformat(),
        },
    }

    return jsonify(payload), 200
