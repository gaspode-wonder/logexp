# filename: logexp/app/bp/about/routes.py

from __future__ import annotations

from typing import Any

from flask import render_template, request

from logexp.app.bp.about import bp_about
from logexp.app.logging_setup import get_logger

logger = get_logger("logexp.about")


@bp_about.route("/")
def about_index() -> Any:
    logger.debug(
        "about_index_requested",
        extra={"path": request.path, "method": request.method},
    )
    return render_template("about.html")
