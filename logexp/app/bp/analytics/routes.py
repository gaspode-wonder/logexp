# logexp/app/bp/analytics/routes.py

import datetime
from flask import (
    render_template,
    request,
    Response,
)

from . import bp_analytics

from logexp.app.analytics import run_analytics, compute_window
from logexp.app.services.analytics_diagnostics import summarize_readings
from logexp.app.services.analytics_export import export_readings_to_csv

@bp_analytics.route("/", methods=["GET"])
def analytics_index():
    # Query params
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    metric = request.args.get("metric", "cpm")
    quick_range = request.args.get("range")

    # Default: last 24h
    if not start_date and not end_date and not quick_range:
        default_start = datetime.now() - datetime.timedelta(hours=24)
        start_date = default_start.isoformat(timespec="minutes")
        end_date = datetime.now().isoformat(timespec="minutes")

    # Handle quick ranges
    if quick_range:
        now = datetime.now()
        if quick_range == "1h":
            start_date = (now - datetime.timedelta(hours=1)).isoformat(timespec="minutes")
        elif quick_range == "24h":
            start_date = (now - datetime.timedelta(hours=24)).isoformat(timespec="minutes")
        elif quick_range == "7d":
            start_date = (now - datetime.timedelta(days=7)).isoformat(timespec="minutes")
        end_date = now.isoformat(timespec="minutes")

    # Run analytics subsystem
    rollup = run_analytics()
    readings = compute_window()
    diagnostics = summarize_readings(readings)

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
def analytics_export():
    readings = compute_window()
    csv_data = export_readings_to_csv(readings)

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=analytics.csv"},
    )
