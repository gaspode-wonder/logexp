import os
import csv
import io
from datetime import datetime, timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from flask import (
    render_template,
    request,
    current_app,
    Response,
)

from logexp.app.models import LogExpReading
from . import bp_analytics


# ------------------------------------------------------------
# /analytics  — main analytics dashboard
# ------------------------------------------------------------
@bp_analytics.route("/", methods=["GET"])
def analytics_index():
    # Query params
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    metric = request.args.get("metric", "cpm")
    quick_range = request.args.get("range")

    # Default: last 24h if no params
    if not start_date and not end_date and not quick_range:
        default_start = datetime.now() - timedelta(hours=24)
        start_date = default_start.isoformat(timespec="minutes")
        end_date = datetime.now().isoformat(timespec="minutes")

    # Handle quick ranges
    if quick_range:
        now = datetime.now()
        if quick_range == "1h":
            start_date = (now - timedelta(hours=1)).isoformat(timespec="minutes")
        elif quick_range == "24h":
            start_date = (now - timedelta(hours=24)).isoformat(timespec="minutes")
        elif quick_range == "7d":
            start_date = (now - timedelta(days=7)).isoformat(timespec="minutes")
        end_date = now.isoformat(timespec="minutes")

    # Build query
    query = LogExpReading.query
    if start_date:
        try:
            query = query.filter(
                LogExpReading.timestamp >= datetime.fromisoformat(start_date)
            )
        except ValueError:
            current_app.logger.warning(f"Invalid start_date: {start_date}")

    if end_date:
        try:
            query = query.filter(
                LogExpReading.timestamp <= datetime.fromisoformat(end_date)
            )
        except ValueError:
            current_app.logger.warning(f"Invalid end_date: {end_date}")

    readings = query.order_by(LogExpReading.timestamp).all()

    # Chart generation
    chart_url = None
    if readings:
        try:
            timestamps = [r.timestamp for r in readings]

            if metric == "cps":
                values = [r.counts_per_second for r in readings]
                ylabel = "Counts per Second (CPS)"
            elif metric == "usvh":
                values = [r.microsieverts_per_hour for r in readings]
                ylabel = "µSv/h"
            else:
                values = [r.counts_per_minute for r in readings]
                ylabel = "Counts per Minute (CPM)"

            plt.figure(figsize=(8, 4))
            plt.plot(timestamps, values, marker="o", linestyle="-", color="blue")
            plt.title(f"{ylabel} Over Time")
            plt.xlabel("Timestamp")
            plt.ylabel(ylabel)
            plt.xticks(rotation=45)
            plt.tight_layout()

            static_path = os.path.join(
                current_app.root_path, "static", "analytics.png"
            )
            plt.savefig(static_path)
            plt.close()

            chart_url = "/static/analytics.png"

        except Exception as e:
            current_app.logger.error(f"Chart generation failed: {e}")

    return render_template(
        "analytics.html",
        readings=readings,
        chart_url=chart_url,
        start_date=start_date,
        end_date=end_date,
        metric=metric,
    )


# ------------------------------------------------------------
# /analytics/export — CSV export
# ------------------------------------------------------------
@bp_analytics.route("/export", methods=["GET"])
def analytics_export():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    metric = request.args.get("metric", "cpm")
    quick_range = request.args.get("range")

    # Default: last 24h if no params
    if not start_date and not end_date and not quick_range:
        default_start = datetime.now() - timedelta(hours=24)
        start_date = default_start.isoformat(timespec="minutes")
        end_date = datetime.now().isoformat(timespec="minutes")

    # Handle quick ranges
    if quick_range:
        now = datetime.now()
        if quick_range == "1h":
            start_date = (now - timedelta(hours=1)).isoformat(timespec="minutes")
        elif quick_range == "24h":
            start_date = (now - timedelta(hours=24)).isoformat(timespec="minutes")
        elif quick_range == "7d":
            start_date = (now - timedelta(days=7)).isoformat(timespec="minutes")
        end_date = now.isoformat(timespec="minutes")

    # Query DB
    query = LogExpReading.query
    if start_date:
        query = query.filter(
            LogExpReading.timestamp >= datetime.fromisoformat(start_date)
        )
    if end_date:
        query = query.filter(
            LogExpReading.timestamp <= datetime.fromisoformat(end_date)
        )

    readings = query.order_by(LogExpReading.timestamp).all()

    # Build CSV
    def generate():
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["Timestamp", "CPS", "CPM", "µSv/h", "Mode"])
        for r in readings:
            writer.writerow(
                [
                    r.timestamp,
                    r.counts_per_second,
                    r.counts_per_minute,
                    r.microsieverts_per_hour,
                    r.mode,
                ]
            )

        yield output.getvalue()


    return Response(
        generate(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=analytics.csv"},
    )
