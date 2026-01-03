from typing import Any

from flask import current_app, redirect, render_template, request, url_for

from logexp.app.bp.settings import bp_settings
from logexp.app.geiger import list_serial_ports


@bp_settings.get("/")
def settings_index() -> Any:
    ports = list_serial_ports()
    configured_port = current_app.config["GEIGER_PORT"]
    baudrate = current_app.config["GEIGER_BAUDRATE"]
    return render_template(
        "settings.html",
        ports=ports,
        configured_port=configured_port,
        baudrate=baudrate,
    )


@bp_settings.post("/")
def update_settings() -> Any:
    selected_port = request.form.get("port")
    selected_baudrate = request.form.get("baudrate", "9600")
    current_app.config["GEIGER_PORT"] = selected_port
    current_app.config["GEIGER_BAUDRATE"] = int(selected_baudrate)
    return redirect(url_for("settings.settings_index"))
