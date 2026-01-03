# filename: logexp/analytics/engine.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Tuple


@dataclass
class ReadingSample:
    timestamp: datetime
    value: float


@dataclass
class AnalyticsResult:
    window_minutes: int
    count: int
    window_start: datetime
    window_end: datetime
    average: Optional[float]
    minimum: Optional[float]
    maximum: Optional[float]


class AnalyticsEngine:
    """
    Stateful, pure analytics engine.

    - Holds an in-memory list of ReadingSample objects.
    - Applies a sliding time window based on `window_minutes`.
    - Computes basic statistics (count, min, max, average) over the window.
    - Rejects naive datetimes (must be timezone-aware).
    """

    def __init__(self, window_minutes: int) -> None:
        if window_minutes <= 0:
            raise ValueError("window_minutes must be positive")

        self.window_minutes: int = window_minutes
        self._samples: List[ReadingSample] = []

    @staticmethod
    def _ensure_aware(dt: datetime) -> None:
        """
        Ensure the datetime is timezone-aware.
        """
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            raise ValueError("datetime must be timezone-aware")

    def add_reading(self, sample: ReadingSample) -> None:
        """
        Add a single reading to the engine.
        """
        self._ensure_aware(sample.timestamp)
        self._samples.append(sample)

    def add_readings(self, samples: List[ReadingSample]) -> None:
        """
        Add multiple readings to the engine.
        """
        for sample in samples:
            self.add_reading(sample)

    def _window_bounds(self, now: datetime) -> Tuple[datetime, datetime]:
        """
        Compute the inclusive window bounds for the given timestamp.
        """
        self._ensure_aware(now)
        window_end: datetime = now
        window_start: datetime = now - timedelta(minutes=self.window_minutes)
        return window_start, window_end

    def get_window(self, now: datetime) -> List[ReadingSample]:
        """
        Return all readings within the inclusive time window:

            [now - window_minutes, now]

        Both boundaries are inclusive.
        """
        window_start, window_end = self._window_bounds(now)

        return [s for s in self._samples if window_start <= s.timestamp <= window_end]

    def compute_metrics(self, now: datetime) -> AnalyticsResult:
        """
        Compute statistics over the current window:

        - count
        - average
        - minimum
        - maximum

        If no samples are in the window, returns zeros/nones as appropriate.
        """
        window_start, window_end = self._window_bounds(now)
        window_samples: List[ReadingSample] = self.get_window(now)

        if not window_samples:
            return AnalyticsResult(
                window_minutes=self.window_minutes,
                count=0,
                window_start=window_start,
                window_end=window_end,
                average=None,
                minimum=None,
                maximum=None,
            )

        values: List[float] = [s.value for s in window_samples]
        count: int = len(values)
        average: float = sum(values) / count
        minimum: float = min(values)
        maximum: float = max(values)

        return AnalyticsResult(
            window_minutes=self.window_minutes,
            count=count,
            window_start=window_start,
            window_end=window_end,
            average=average,
            minimum=minimum,
            maximum=maximum,
        )
