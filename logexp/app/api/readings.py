@bp.get("/api/readings")
def get_readings() -> Any:
    readings = LogExpReading.query.order_by(LogExpReading.timestamp.asc()).all()
    responses = [ReadingResponse(**r.to_dict()).model_dump() for r in readings]
    return jsonify(responses)
