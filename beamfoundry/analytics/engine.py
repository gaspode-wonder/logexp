# filename: analytics/engine.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, List

# ---------------------------------------------------------------------------
# Data structures required by tests
# ---------------------------------------------------------------------------


@dataclass
class ReadingSample:
    timestamp: datetime
    value: float


@dataclass
class AnalyticsResult:
    count: int
    average: float | None
    minimum: float | None
    maximum: float | None
    readings: List[ReadingSample]
    window_start: datetime | None
    window_end: datetime | None


# ---------------------------------------------------------------------------
# Analytics Engine (stateful + stateless API)
# ---------------------------------------------------------------------------


class AnalyticsEngine:
    def __init__(self, window_minutes: float = 5):
        self.window_seconds = window_minutes * 60
        self._samples: List[ReadingSample] = []

    # -----------------------------
    # Stateful ingestion
    # -----------------------------
    def add_reading(self, sample: ReadingSample):
        if sample.timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        self._samples.append(sample)

    def add_readings(self, samples: Iterable[ReadingSample]):
        for s in samples:
            self.add_reading(s)

    # -----------------------------
    # Window extraction
    # -----------------------------
    def get_window(self, now: datetime) -> List[ReadingSample]:
        if now.tzinfo is None:
            raise ValueError("now must be timezone-aware")

        start = now - timedelta(seconds=self.window_seconds)
        end = now

        return [s for s in self._samples if start <= s.timestamp <= end]

    # -----------------------------
    # Metrics
    # -----------------------------
    def compute_metrics(self, now: datetime) -> AnalyticsResult:
        if now.tzinfo is None:
            raise ValueError("now must be timezone-aware")

        start = now - timedelta(seconds=self.window_seconds)
        end = now
        window = self.get_window(now)

        if not window:
            return AnalyticsResult(
                count=0,
                average=None,
                minimum=None,
                maximum=None,
                readings=[],
                window_start=start,
                window_end=end,
            )

        values = [s.value for s in window]

        return AnalyticsResult(
            count=len(window),
            average=sum(values) / len(values),
            minimum=min(values),
            maximum=max(values),
            readings=window,
            window_start=start,
            window_end=end,
        )

    # -----------------------------
    # Stateless API used by tests/test_analytics.py
    # -----------------------------
    def run(self, readings: Iterable[ReadingSample], now: datetime) -> List[ReadingSample]:
        if now.tzinfo is None:
            raise ValueError("now must be timezone-aware")

        start = now - timedelta(seconds=self.window_seconds)
        end = now

        windowed = [r for r in readings if start <= r.timestamp <= end]

        return sorted(windowed, key=lambda r: r.timestamp)
