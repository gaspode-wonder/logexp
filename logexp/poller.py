# logexp/poller.py

import logging

logger = logging.getLogger(__name__)


class Poller:
    """
    Step 11E — Poller implementation.

    11E‑1: skeleton
    11E‑2: poll_once()
    11E‑3: poll_forever() loop (deterministic, test‑safe)
    """

    def __init__(self, config, ingestion):
        self.config = config
        self.ingestion = ingestion

    # ------------------------------------------------------------
    # 11E‑2: Deterministic fake frame provider
    # ------------------------------------------------------------
    def get_frame(self):
        fake_value = self.config.get("FAKE_FRAME_VALUE", 42)
        return {"value": fake_value}

    # ------------------------------------------------------------
    # 11E‑2: poll_once()
    # ------------------------------------------------------------
    def poll_once(self):
        frame = self.get_frame()
        self.ingestion.ingest(frame)
        return frame

    # ------------------------------------------------------------
    # 11E‑3: poll_forever()
    # ------------------------------------------------------------
    def poll_forever(self):
        """
        Loop around poll_once() a finite number of times.

        This is intentionally deterministic and test‑safe.
        No threads, no hardware, no serial.
        """
        max_frames = self.config.get("MAX_FRAMES", 10)

        for _ in range(max_frames):
            self.poll_once()
