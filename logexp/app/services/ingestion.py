# filename: logexp/app/services/ingestion.py
# Step 11D-3: Ingestion pipeline restoration

from __future__ import annotations

from datetime import datetime, timezone
from flask import request, jsonify
from logexp.app.extensions import db
from logexp.app.logging_setup import get_logger
from logexp.validation.ingestion_validator import validate_ingestion_payload
from logexp.app.models import LogExpReading

log = get_logger("logexp.services.ingestion")


def register_ingestion_routes(bp):
    """
    Register the ingestion endpoint on the provided Blueprint.
    """

    @bp.route("/ingest", methods=["POST"])
    def ingest():
        """
        Ingest a single reading.

        Steps:
        1. Parse JSON
        2. Validate payload
        3. Normalize timestamp to UTC
        4. Insert into DB
        5. Return success
        """

        payload = request.get_json(silent=True)
        if payload is None:
            log.warning("invalid_json")
            return jsonify({"error": "invalid JSON"}), 400

        validated = validate_ingestion_payload(payload)
        if validated is None:
            # Validator already logged the reason
            return jsonify({"error": "invalid payload"}), 400

        # ------------------------------------------------------------
        # Normalize timestamp → canonical UTC datetime
        # ------------------------------------------------------------
        try:
            ts = datetime.fromisoformat(validated["timestamp"])
        except Exception:
            log.warning("invalid_timestamp_format", extra={"value": validated["timestamp"]})
            return jsonify({"error": "invalid timestamp"}), 400

        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        else:
            ts = ts.astimezone(timezone.utc)

        # ------------------------------------------------------------
        # Create model instance (model-level validators run here)
        # ------------------------------------------------------------
        reading = LogExpReading(
            timestamp=ts,
            counts_per_second=float(validated["cps"]),
            counts_per_minute=float(validated["cpm"]),
            microsieverts_per_hour=float(validated["usv"]),
            mode=validated["mode"],
        )

        db.session.add(reading)
        db.session.commit()

        return jsonify({"status": "ok", "id": reading.id}), 201
