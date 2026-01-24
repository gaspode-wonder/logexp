# filename: logexp/app/bp/docs/routes.py

from __future__ import annotations

from typing import Any

from flask import render_template, request
from flask_login import login_required

from ...logging_setup import get_logger
from . import bp_docs

logger = get_logger("beamfoundry.docs")


@bp_docs.route("/")
@login_required
def docs_index() -> Any:
    logger.debug(
        "docs_index_requested",
        extra={"path": request.path, "method": request.method},
    )
    return render_template("docs.html")


@bp_docs.route("/timezone")
def timezone_policy() -> Any:
    logger.debug(
        "docs_timezone_requested",
        extra={"path": request.path, "method": request.method},
    )
    return render_template("docs/timezone.html")
