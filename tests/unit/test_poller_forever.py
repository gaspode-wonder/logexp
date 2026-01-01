# tests/unit/test_poller_forever.py

from logexp.poller import Poller


class FakeIngestion:
    def __init__(self):
        self.received = []

    def ingest(self, frame):
        self.received.append(frame)


def test_poll_forever_calls_poll_once_repeatedly():
    # Arrange
    config = {
        "FAKE_FRAME_VALUE": 7,
        "MAX_FRAMES": 5,
    }
    ingestion = FakeIngestion()
    poller = Poller(config=config, ingestion=ingestion)

    # Act
    poller.poll_forever()

    # Assert
    assert len(ingestion.received) == 5
    assert ingestion.received == [{"value": 7}] * 5
