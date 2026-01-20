# filename: logexp/app/bp/analytics/routes.py

from __future__ import annotations

import datetime
from typing import Any

from flask import Response, render_template, request
from flask_login import login_required

from app.bp.analytics import bp_analytics
from app.extensions import db
from app.logging_setup import get_logger
from app.services.analytics import compute_window, run_analytics
from app.services.analytics_export import export_readings_to_csv
from app.services.analytics_readings import summarize_readings

logger = get_logger("beamfoundry.analytics")


@bp_analytics.route("/", methods=["GET"])
@login_required
def analytics_index() -> Any:
    logger.debug(
        "analytics_index_requested",
        extra={
            "args": dict(request.args),
            "path": request.path,
            "method": request.method,
        },
    )

    # Query params
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    metric = request.args.get("metric", "cpm")
    quick_range = request.args.get("range")

    # Default: last 24h
    if not start_date and not end_date and not quick_range:
        default_start = datetime.datetime.now() - datetime.timedelta(hours=24)
        start_date = default_start.isoformat(timespec="minutes")
        end_date = datetime.datetime.now().isoformat(timespec="minutes")

        logger.debug(
            "analytics_index_default_range",
            extra={"start_date": start_date, "end_date": end_date},
        )

    # Handle quick ranges
    if quick_range:
        now = datetime.datetime.now()

        logger.debug(
            "analytics_index_quick_range",
            extra={"quick_range": quick_range, "now": now.isoformat()},
        )

        if quick_range == "1h":
            start_date = (now - datetime.timedelta(hours=1)).isoformat(timespec="minutes")
        elif quick_range == "24h":
            start_date = (now - datetime.timedelta(hours=24)).isoformat(timespec="minutes")
        elif quick_range == "7d":
            start_date = (now - datetime.timedelta(days=7)).isoformat(timespec="minutes")

        end_date = now.isoformat(timespec="minutes")

    # Run analytics subsystem
    rollup = run_analytics(db.session)
    readings = compute_window()
    diagnostics = summarize_readings(readings)

    logger.debug(
        "analytics_index_render",
        extra={
            "rollup_present": rollup is not None,
            "readings_count": len(readings),
            "diagnostics_count": diagnostics.get("count"),
        },
    )

    return render_template(
        "analytics.html",
        rollup=rollup,
        diagnostics=diagnostics,
        readings=readings,
        start_date=start_date,
        end_date=end_date,
        metric=metric,
    )


@bp_analytics.route("/export", methods=["GET"])
def analytics_export() -> Any:
    logger.debug(
        "analytics_export_requested",
        extra={"path": request.path, "method": request.method},
    )

    readings = compute_window()
    csv_data = export_readings_to_csv(readings)

    logger.debug(
        "analytics_export_completed",
        extra={"readings_count": len(readings), "csv_bytes": len(csv_data)},
    )

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=analytics.csv"},
    )
