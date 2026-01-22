# tests/test_config_schema.py

import os
from typing import Any, Dict

from logexp.app.config import load_config


def _with_env(overrides: Dict[str, str]) -> Dict[str, Any]:
    """
    Helper for calling load_config in a way that mimics real env usage.
    """
    # Start from current process env, apply overrides
    env = dict(os.environ)
    env.update(overrides)
    return load_config(overrides=env)


def test_config_accepts_canonical_values() -> None:
    env = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "LOCAL_TIMEZONE": "UTC",
        "GEIGER_THRESHOLD": "50.0",
        "START_POLLER": "False",
        "LOGEXP_NODE_ID": "test-node",
        "TELEMETRY_ENABLED": "True",
        "TELEMETRY_INTERVAL_SECONDS": "30",
    }

    cfg = _with_env(env)

    assert cfg["SQLALCHEMY_DATABASE_URI"].startswith("sqlite://")
    assert cfg["LOCAL_TIMEZONE"] == "UTC"
    assert isinstance(cfg["GEIGER_THRESHOLD"], float)
    assert cfg["GEIGER_THRESHOLD"] == 50.0
    assert cfg["START_POLLER"] is False
    assert cfg["LOGEXP_NODE_ID"] == "test-node"
    assert cfg["TELEMETRY_ENABLED"] is True
    assert cfg["TELEMETRY_INTERVAL_SECONDS"] == 30
