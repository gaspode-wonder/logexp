# logexp/app/bp/diagnostics_runtime/routes.py
from __future__ import annotations

import os
import platform
import sys
import time
from typing import Any, Dict

from flask import Response, jsonify

from . import bp_diagnostics_runtime


def _filtered_env() -> Dict[str, str]:
    """Return a filtered subset of environment variables relevant to diagnostics."""
    keys = ("SQL", "FLASK", "PYTHON", "TZ", "ANALYTICS")
    return {k: v for k, v in os.environ.items() if any(x in k for x in keys)}


@bp_diagnostics_runtime.get("/")
def runtime_diagnostics() -> Response:
    """Return runtime diagnostics as JSON."""
    payload: Dict[str, Any] = {
        "cwd": os.getcwd(),
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "sys_path": list(sys.path),
        "env_filtered": _filtered_env(),
        "timestamp": time.time(),
    }
    return jsonify(payload)
