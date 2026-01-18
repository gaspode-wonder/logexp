# filename: logexp/app/bp/ui/routes.py

from __future__ import annotations

from typing import Any

from flask import current_app, redirect, render_template, request, url_for
from logexp.app.bp.ui import bp_ui
from logexp.app.extensions import db
from logexp.app.logging_setup import get_logger
from logexp.app.models import LogExpReading

logger = get_logger("logexp.ui")


@bp_ui.route("/")
def index() -> Any:
    logger.debug(
        "ui_index_requested",
        extra={"path": request.path, "method": request.method},
    )
    return redirect(url_for("ui.readings_index"))


@bp_ui.route("/readings")
def readings_index() -> Any:
    logger.debug(
        "ui_readings_index_requested",
        extra={"path": request.path, "method": request.method},
    )

    readings = (
        db.session.query(LogExpReading).order_by(LogExpReading.timestamp.desc()).limit(50).all()
    )

    poller = getattr(current_app, "poller", None)
    poller_status = "running" if poller and poller._thread.is_alive() else "stopped"
    local_timezone = current_app.config["LOCAL_TIMEZONE"]

    logger.debug(
        "ui_readings_index_context",
        extra={
            "readings_count": len(readings),
            "poller_status": poller_status,
            "local_timezone": local_timezone,
        },
    )

    return render_template(
        "readings.html",
        readings=readings,
        poller_status=poller_status,
        local_timezone=local_timezone,
    )
