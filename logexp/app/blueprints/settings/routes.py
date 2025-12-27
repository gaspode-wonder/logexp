from flask import render_template, request, current_app
from logexp.app.geiger import list_serial_ports
from . import bp_settings

# Placeholder: move settings routes from app_blueprints.py here.

@bp_settings.route("/", methods=["GET", "POST"])
def settings_index():
    ports = list_serial_ports()
    configured_port = current_app.config["GEIGER_PORT"]
    baudrate = current_app.config["GEIGER_BAUDRATE"]

    if request.method == "POST":
        selected_port = request.form.get("port")
        selected_baud = request.form.get("baudrate")
        if selected_port:
            current_app.config["GEIGER_PORT"] = selected_port
        if selected_baud:
            current_app.config["GEIGER_BAUDRATE"] = int(selected_baud)

    return render_template(
        "settings.html",
        ports=ports,
        configured_port=configured_port,
        baudrate=baudrate,
    )
