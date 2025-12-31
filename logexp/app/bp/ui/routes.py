from flask import current_app, redirect, render_template, url_for

from logexp.app.models import LogExpReading

from . import bp_ui


@bp_ui.route("/")
def index():
    return redirect(url_for("ui.readings_index"))


@bp_ui.route("/readings")
def readings_index():
    readings = (
        LogExpReading.query.order_by(LogExpReading.timestamp.desc()).limit(50).all()
    )
    poller = getattr(current_app, "poller", None)
    poller_status = "running" if poller and poller._thread.is_alive() else "stopped"
    local_timezone = current_app.config["LOCAL_TIMEZONE"]

    return render_template(
        "readings.html",
        readings=readings,
        poller_status=poller_status,
        local_timezone=local_timezone,
    )
