from flask import jsonify, render_template, current_app
from logexp.app.geiger import list_serial_ports, try_port
from . import bp_diagnostics

# Placeholder: move diagnostics routes from app_blueprints.py here.

@bp_diagnostics.route("/")
def diagnostics_index():
    ports = list_serial_ports()
    baudrate = current_app.config["GEIGER_BAUDRATE"]
    results = {p: try_port(p, baudrate) for p in ports}
    return render_template("diagnostics.html", results=results)
