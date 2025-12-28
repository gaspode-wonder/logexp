from flask import render_template, request, current_app, redirect, url_for
from logexp.app.geiger import list_serial_ports
from . import bp_settings

@bp_settings.get("/")
def settings_index():
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
def update_settings():
    selected_port = request.form.get("port")
    selected_baudrate = request.form.get("baudrate", "9600")
    current_app.config["GEIGER_PORT"] = selected_port
    current_app.config["GEIGER_BAUDRATE"] = int(selected_baudrate)
    return redirect(url_for("settings.settings_index"))
