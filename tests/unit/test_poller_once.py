# tests/unit/test_poller_once.py

from logexp.poller import Poller


class FakeIngestion:
    def __init__(self):
        self.received = []

    def ingest(self, frame):
        self.received.append(frame)


def test_poll_once_returns_frame_and_calls_ingestion():
    # Arrange
    config = {"FAKE_FRAME_VALUE": 123}
    ingestion = FakeIngestion()
    poller = Poller(config=config, ingestion=ingestion)

    # Act
    frame = poller.poll_once()

    # Assert
    assert frame == {"value": 123}
    assert ingestion.received == [{"value": 123}]
    assert len(ingestion.received) == 1
