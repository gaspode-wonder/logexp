from flask import jsonify, Response
from logexp.app.models import LogExpReading
from . import bp_api

# Placeholder: move API routes from app_blueprints.py here.

@bp_api.route("/readings")
def api_readings():
    readings = LogExpReading.query.order_by(LogExpReading.id.desc()).limit(100).all()
    return jsonify([r.to_dict() for r in readings])
