# filename: tests/fixtures/poller/fake_ingestion.py

from __future__ import annotations

from typing import Any, Dict, List, Optional


class FakeIngestion:
    """
    Deterministic ingestion sink.

    - Records every attempted frame in `frames`
    - Records failures in `failures`
    - Simulates immediate or delayed ingestion failures
    """

    def __init__(self, should_fail: bool = False, fail_after: Optional[int] = None):
        self.should_fail: bool = should_fail
        self.fail_after: Optional[int] = fail_after
        self.frames: List[Dict[str, Any]] = []
        self.failures: int = 0

    def ingest(self, frame: Dict[str, Any]) -> None:
        # Always record the attempted frame
        self.frames.append(frame)

        # Immediate failure mode
        if self.should_fail:
            self.failures += 1
            raise RuntimeError("fake_ingestion_failure")

        # Delayed failure mode
        if self.fail_after is not None and len(self.frames) > self.fail_after:
            self.failures += 1
            raise RuntimeError("fake_ingestion_failure_after_limit")
