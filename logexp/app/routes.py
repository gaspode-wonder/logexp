from flask import Blueprint, jsonify, request, render_template
from logexp.app import db
from logexp.app.models import LogExpReading
from logexp.app.schemas import ReadingCreate, ReadingResponse
from typing import Any

bp = Blueprint("readings", __name__)

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
