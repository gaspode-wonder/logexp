# filename: logexp/app/bp/settings/routes.py

from __future__ import annotations

from typing import Any

from flask import current_app, redirect, render_template, request, url_for

from app.bp.settings import bp_settings
from app.geiger import list_serial_ports
from app.logging_setup import get_logger

logger = get_logger("logexp.settings")


@bp_settings.get("/")
def settings_index() -> Any:
    logger.debug(
        "settings_index_requested",
        extra={"path": request.path, "method": request.method},
    )

    ports = list_serial_ports()
    configured_port = current_app.config["GEIGER_PORT"]
    baudrate = current_app.config["GEIGER_BAUDRATE"]

    logger.debug(
        "settings_index_context",
        extra={
            "ports_count": len(ports),
            "configured_port": configured_port,
            "baudrate": baudrate,
        },
    )

    return render_template(
        "settings.html",
        ports=ports,
        configured_port=configured_port,
        baudrate=baudrate,
    )


@bp_settings.post("/")
def update_settings() -> Any:
    logger.debug(
        "settings_update_requested",
        extra={"path": request.path, "method": request.method},
    )

    selected_port = request.form.get("port")
    selected_baudrate = request.form.get("baudrate", "9600")

    current_app.config["GEIGER_PORT"] = selected_port
    current_app.config["GEIGER_BAUDRATE"] = int(selected_baudrate)

    logger.debug(
        "settings_updated",
        extra={
            "selected_port": selected_port,
            "selected_baudrate": selected_baudrate,
        },
    )

    return redirect(url_for("settings.settings_index"))
