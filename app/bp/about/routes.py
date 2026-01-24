# filename: logexp/app/bp/about/routes.py

from __future__ import annotations

from typing import Any

from flask import render_template, request

from ...logging_setup import get_logger
from . import bp_about

logger = get_logger("beamfoundry.about")


@bp_about.route("/")
def about_index() -> Any:
    logger.debug(
        "about_index_requested",
        extra={"path": request.path, "method": request.method},
    )
    return render_template("about.html")
