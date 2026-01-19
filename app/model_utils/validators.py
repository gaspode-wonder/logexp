# filename: logexp/app/models/validators.py

"""
SQLAlchemy model-level validation hooks for LogExpReading.

Enforces:
  - Non-negative numeric fields (cps, cpm, usv)
  - Valid mode values: SLOW, FAST, INST
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import validates

from app.logging_setup import get_logger

log = get_logger(__name__)


class ReadingValidators:
    """
    Model-level validation mixin for LogExpReading.

    SQLAlchemy automatically invokes these hooks when ORM attributes
    are assigned, ensuring correctness before persistence.
    """

    @validates("cps", "cpm")
    def validate_counts(self, key: str, value: Any) -> float:
        try:
            numeric = float(value)
        except Exception:
            raise ValueError(f"{key} must be numeric")

        if numeric < 0:
            raise ValueError(f"{key} must be non-negative")

        return numeric

    @validates("usv")
    def validate_usv(self, key: str, value: Any) -> float:
        try:
            numeric = float(value)
        except Exception:
            raise ValueError("usv must be numeric")

        if numeric < 0:
            raise ValueError("usv must be non-negative")

        return numeric

    @validates("mode")
    def validate_mode(self, key: str, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError(f"invalid mode: {value!r}")

        mode_up = value.strip().upper()
        if mode_up not in ("SLOW", "FAST", "INST"):
            raise ValueError(f"invalid mode: {value}")

        return mode_up
