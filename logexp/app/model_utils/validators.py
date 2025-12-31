# filename: logexp/app/models/validators.py
"""
SQLAlchemy model-level validation hooks.
"""
from sqlalchemy.orm import validates

from logexp.logging import get_logger

log = get_logger(__name__)


class ReadingValidators:
    @validates("cps", "cpm")
    def validate_counts(self, key, value):
        if value < 0:
            raise ValueError(f"{key} must be non-negative")
        return value

    @validates("usv")
    def validate_usv(self, key, value):
        if value < 0:
            raise ValueError("usv must be non-negative")
        return value

    @validates("mode")
    def validate_mode(self, key, value):
        if value not in ("SLOW", "FAST", "INST"):
            raise ValueError(f"invalid mode: {value}")
        return value
