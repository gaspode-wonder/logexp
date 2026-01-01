# logexp/poller.py

import logging

logger = logging.getLogger(__name__)


class Poller:
    """
    Step 11E — Poller implementation (11E‑2: poll_once).

    This version implements a deterministic, test‑safe poll_once()
    using a fake frame provider. No hardware, no serial, no threads.
    """

    def __init__(self, config, ingestion):
        self.config = config
        self.ingestion = ingestion

    # ------------------------------------------------------------
    # 11E‑2: Deterministic fake frame provider
    # ------------------------------------------------------------
    def get_frame(self):
        """
        Return a deterministic fake frame for testing.

        Later steps (11E‑4+) will replace this with real serial input.
        """
        fake_value = self.config.get("FAKE_FRAME_VALUE", 42)
        return {"value": fake_value}

    # ------------------------------------------------------------
    # 11E‑2: Implement poll_once()
    # ------------------------------------------------------------
    def poll_once(self):
        """
        Read one frame and hand it to ingestion.
        """
        frame = self.get_frame()

        # Ingestion is responsible for validation and persistence.
        self.ingestion.ingest(frame)

        return frame

    # ------------------------------------------------------------
    # 11E‑1: Still unimplemented
    # ------------------------------------------------------------
    def poll_forever(self):
        raise NotImplementedError("poll_forever() not yet implemented")
