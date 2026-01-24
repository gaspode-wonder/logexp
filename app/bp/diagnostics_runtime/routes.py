# filename: logexp/app/bp/diagnostics_runtime/routes.py

from __future__ import annotations

import os
import platform
import sys
import time
from typing import Any, Dict

from flask import Response, jsonify, request
from flask_login import login_required

from ...logging_setup import get_logger
from . import bp_diagnostics_runtime

logger = get_logger("beamfoundry.diagnostics.runtime")


def _filtered_env() -> Dict[str, str]:
    """Return a filtered subset of environment variables relevant to diagnostics."""
    keys = ("SQL", "FLASK", "PYTHON", "TZ", "ANALYTICS")
    filtered = {k: v for k, v in os.environ.items() if any(x in k for x in keys)}

    logger.debug(
        "runtime_diag_env_filtered",
        extra={"count": len(filtered)},
    )

    return filtered


@bp_diagnostics_runtime.get("/")
@login_required
def runtime_diagnostics() -> Response:
    """Return runtime diagnostics as JSON."""
    logger.debug(
        "runtime_diag_requested",
        extra={"path": request.path, "method": request.method},
    )

    payload: Dict[str, Any] = {
        "cwd": os.getcwd(),
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "sys_path": list(sys.path),
        "env_filtered": _filtered_env(),
        "timestamp": time.time(),
    }

    logger.debug(
        "runtime_diag_payload_built",
        extra={"keys": list(payload.keys())},
    )

    return jsonify(payload)
