# logexp/app/model_utils/reading_validator.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

ValidMode = Literal["SLOW", "FAST", "INST"]


@dataclass(slots=True)
class ReadingValidator:
    timestamp: datetime
    value: float
    mode: ValidMode

    @classmethod
    def from_raw(cls, *, timestamp, value, mode):
        ts = cls._normalize_timestamp(timestamp)
        val = cls._normalize_value(value)
        mode_norm = cls._normalize_mode(mode)
        return cls(timestamp=ts, value=val, mode=mode_norm)

    @staticmethod
    def _normalize_timestamp(ts):
        if isinstance(ts, datetime):
            if ts.tzinfo is None:
                return ts.replace(tzinfo=timezone.utc)
            return ts.astimezone(timezone.utc)

        if isinstance(ts, str):
            parsed = datetime.fromisoformat(ts)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)

        raise TypeError("Invalid timestamp")

    @staticmethod
    def _normalize_value(val):
        try:
            return float(val)
        except Exception:
            raise ValueError("Invalid numeric value")

    @staticmethod
    def _normalize_mode(mode: str) -> ValidMode:
        mode_up = mode.strip().upper()
        if mode_up not in ("SLOW", "FAST", "INST"):
            raise ValueError(f"Invalid mode: {mode}")
        return mode_up
