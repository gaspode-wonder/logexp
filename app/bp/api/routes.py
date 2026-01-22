# logexp/app/bp/api/route.py
from __future__ import annotations

from typing import Any

from flask import current_app, jsonify, request
from flask.typing import ResponseReturnValue
from flask_login import login_required
from sqlalchemy import desc

from . import bp_api
from ...extensions import db
from ...geiger import list_serial_ports, read_geiger, try_port
from ...logging_setup import get_logger
from ...models import LogExpReading
from ...schemas import ReadingCreate, ReadingResponse

logger = get_logger("beamfoundry.api")


@bp_api.get("/readings")
def get_readings() -> Any:
    logger.debug(
        "api_get_readings_requested",
        extra={"path": request.path, "method": request.method},
    )

    readings = db.session.query(LogExpReading).order_by(LogExpReading.timestamp.asc()).all()

    responses = [ReadingResponse(**r.to_dict()).model_dump(exclude_none=False) for r in readings]

    logger.debug(
        "api_get_readings_returning",
        extra={"count": len(responses)},
    )

    return jsonify(responses)


@bp_api.post("/readings")
def create_reading() -> Any:
    logger.debug(
        "api_create_reading_requested",
        extra={"path": request.path, "method": request.method},
    )

    payload = request.get_json(force=True, silent=True) or {}

    try:
        validated = ReadingCreate(**payload)
    except Exception as e:
        logger.debug(
            "api_create_reading_validation_failed",
            extra={"error": str(e)},
        )
        return jsonify({"error": str(e)}), 400

    reading = LogExpReading(
        counts_per_second=validated.counts_per_second,
        counts_per_minute=validated.counts_per_minute,
        microsieverts_per_hour=validated.microsieverts_per_hour,
        mode=validated.mode,
        device_id=validated.device_id,
    )

    db.session.add(reading)
    db.session.commit()

    logger.debug(
        "api_create_reading_committed",
        extra={"id": reading.id},
    )

    response = ReadingResponse(**reading.to_dict())
    return jsonify(response.model_dump(exclude_none=False)), 201


@bp_api.get("/readings/latest")
def get_latest_reading() -> ResponseReturnValue:
    logger.debug(
        "api_get_latest_reading_requested",
        extra={"path": request.path, "method": request.method},
    )

    row = db.session.query(LogExpReading).order_by(desc(LogExpReading.timestamp)).first()

    if row is None:
        logger.debug("api_get_latest_reading_no_rows")
        return jsonify({"error": "no readings available"}), 404

    response = ReadingResponse(**row.to_dict())
    payload = response.model_dump(exclude_none=False)

    logger.debug(
        "api_get_latest_reading_returning",
        extra={"id": payload.get("id"), "device_id": payload.get("device_id")},
    )

    return jsonify(payload), 200


@bp_api.get("/readings.json")
def readings_json() -> Any:
    logger.debug(
        "api_readings_json_requested",
        extra={"path": request.path, "method": request.method},
    )

    readings = (
        db.session.query(LogExpReading).order_by(LogExpReading.timestamp.desc()).limit(50).all()
    )

    logger.debug(
        "api_readings_json_returning",
        extra={"count": len(readings)},
    )

    return jsonify([r.to_dict() for r in readings])


@bp_api.get("/geiger")
def geiger_live() -> Any:
    logger.debug(
        "api_geiger_live_requested",
        extra={"path": request.path, "method": request.method},
    )

    try:
        data = read_geiger(
            current_app.config["GEIGER_PORT"],
            current_app.config["GEIGER_BAUDRATE"],
        )
        logger.debug("api_geiger_live_success")
        return jsonify({"raw": data}), 200
    except Exception as e:
        logger.error(
            "api_geiger_live_error",
            extra={"error": str(e)},
        )
        return jsonify({"error": str(e)}), 500


@bp_api.post("/geiger/push")
def geiger_push() -> Any:
    logger.debug(
        "api_geiger_push_requested",
        extra={"path": request.path, "method": request.method},
    )

    payload = request.get_json(force=True, silent=True) or {}

    try:
        validated = ReadingCreate(**payload)
    except Exception as e:
        logger.debug(
            "api_geiger_push_validation_failed",
            extra={"error": str(e)},
        )
        return jsonify({"error": str(e)}), 400

    reading = LogExpReading(
        counts_per_second=validated.counts_per_second,
        counts_per_minute=validated.counts_per_minute,
        microsieverts_per_hour=validated.microsieverts_per_hour,
        mode=validated.mode,
        device_id=validated.device_id,
    )

    db.session.add(reading)
    db.session.commit()

    logger.debug(
        "api_geiger_push_committed",
        extra={"id": reading.id},
    )

    response = ReadingResponse(**reading.to_dict())
    return jsonify(response.model_dump(exclude_none=False)), 201


@bp_api.get("/geiger/test")
def geiger_test() -> Any:
    logger.debug(
        "api_geiger_test_requested",
        extra={"path": request.path, "method": request.method},
    )

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
        logger.debug("api_geiger_test_no_ports")
        return jsonify({"error": "No serial ports detected"}), 404

    logger.debug(
        "api_geiger_test_complete",
        extra={"port_count": len(ports)},
    )

    return jsonify(results)


@bp_api.get("/poller/status")
def poller_status() -> Any:
    logger.debug(
        "api_poller_status_requested",
        extra={"path": request.path, "method": request.method},
    )

    poller = getattr(current_app, "poller", None)
    status = "running" if poller and poller._thread.is_alive() else "stopped"

    logger.debug(
        "api_poller_status_returning",
        extra={"status": status},
    )

    return jsonify({"status": status})


@bp_api.post("/poller/start")
def poller_start() -> Any:
    logger.debug(
        "api_poller_start_requested",
        extra={"path": request.path, "method": request.method},
    )

    poller = getattr(current_app, "poller", None)
    if poller and not poller._thread.is_alive():
        poller.start()
        logger.debug("api_poller_started")
        return jsonify({"status": "started"})

    logger.debug("api_poller_start_already_running")
    return jsonify({"status": "already running"})


@bp_api.post("/poller/stop")
def poller_stop() -> Any:
    logger.debug(
        "api_poller_stop_requested",
        extra={"path": request.path, "method": request.method},
    )

    poller = getattr(current_app, "poller", None)
    if poller and poller._thread.is_alive():
        poller.stop()
        logger.debug("api_poller_stopped")
        return jsonify({"status": "stopped"})

    logger.debug("api_poller_stop_not_running")
    return jsonify({"status": "not running"})


@bp_api.get("/health")
def health() -> Any:
    logger.debug(
        "api_health_requested",
        extra={"path": request.path, "method": request.method},
    )
    return jsonify({"status": "ok"}), 200


@bp_api.get("/diagnostics")
def diagnostics_api() -> Any:
    logger.debug(
        "api_diagnostics_requested",
        extra={"path": request.path, "method": request.method},
    )

    from datetime import datetime, timezone

    from ...services.analytics_diagnostics import get_analytics_status
    from ...services.database_diagnostics import get_database_status
    from ...services.ingestion import get_ingestion_status
    from ...services.poller import get_poller_status

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

    logger.debug(
        "api_diagnostics_completed",
        extra={
            "ingestion": payload["ingestion"],
            "poller": payload["poller"],
            "analytics": payload["analytics"],
            "database": payload["database"],
        },
    )

    return jsonify(payload), 200
