# logexp/poller.py

import logging

logger = logging.getLogger(__name__)


class Poller:
    """
    Step 11E — Poller skeleton.

    This class provides the structure for a simplified ingestion source.
    No hardware access, no serial usage, and no ingestion integration yet.
    """

    def __init__(self, config, ingestion):
        self.config = config
        self.ingestion = ingestion

    def poll_once(self):
        """
        Read one frame and hand it to ingestion.
        Implementation added in later 11E commits.
        """
        raise NotImplementedError("poll_once() not yet implemented")

    def poll_forever(self):
        """
        Loop around poll_once().
        Implementation added in later 11E commits.
        """
        raise NotImplementedError("poll_forever() not yet implemented")
